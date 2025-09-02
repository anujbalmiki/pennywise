"use client"

import { useRef, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuthedFetcher } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/components/auth/auth-provider"

async function readFileAsText(file: File) {
  return await file.text()
}
function parseCSV(text: string) {
  const lines = text.split(/\r?\n/).filter(Boolean)
  if (lines.length === 0) return []
  const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""))
  const rows = lines.slice(1).map((line) => {
    const cols = line.split(",").map((c) => c.trim().replace(/^"|"$/g, ""))
    const obj: Record<string, string> = {}
    headers.forEach((h, i) => (obj[h] = cols[i] ?? ""))
    return obj
  })
  return rows
}
function parseXML(text: string) {
  const doc = new DOMParser().parseFromString(text, "application/xml")
  const txNodes = Array.from(doc.getElementsByTagName("transaction"))
  const rows = txNodes.length ? txNodes : Array.from(doc.getElementsByTagName("item"))
  return rows.map((n) => {
    const get = (tag: string) => n.getElementsByTagName(tag)[0]?.textContent?.trim() || ""
    return {
      Date: get("Date") || get("date"),
      Amount: get("Amount") || get("amount"),
      Description: get("Description") || get("description") || get("Merchant") || get("merchant"),
      Type: get("Type") || get("type"),
      Mode: get("Mode") || get("mode"),
      Remarks: get("Remarks") || get("remarks"),
    }
  })
}
function parseTXT(text: string) {
  // Expect lines like: 2025-01-15,500.00,Amazon Purchase,Debit
  const rows: any[] = []
  for (const line of text.split(/\r?\n/)) {
    const t = line.trim()
    if (!t) continue
    const parts = t.split(",")
    rows.push({
      Date: parts[0]?.trim() || "",
      Amount: parts[1]?.trim() || "",
      Description: parts[2]?.trim() || "",
      Type: parts[3]?.trim() || "",
    })
  }
  return rows
}
function normalizeToTransactions(rows: any[]) {
  // Map generic rows to transaction-like JSON expected by backend
  return rows.map((r) => {
    const amount = Number(r.Amount ?? r.amount ?? r.amt ?? 0)
    const tsRaw = r.Date ?? r.date ?? r.Timestamp ?? r.ts
    const tsIso = tsRaw ? new Date(tsRaw).toISOString() : new Date().toISOString()
    return {
      ts: tsIso,
      amount,
      merchant: r.Description ?? r.description ?? r.Merchant ?? r.merchant ?? "",
      category: r.Type ?? r.type ?? "",
      mode: r.Mode ?? r.mode ?? "",
      remarks: r.Remarks ?? r.remarks ?? "",
      failed: false,
    }
  })
}

export function ImportPanel() {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [loading, setLoading] = useState(false)
  const fetcher = useAuthedFetcher()
  const { toast } = useToast()
  const { getIdToken } = useAuth()

  async function onUpload(kind: "csv" | "xml" | "txt") {
    const file = inputRef.current?.files?.[0]
    if (!file) {
      toast({ title: "Select a file first", variant: "destructive" })
      return
    }
    setLoading(true)
    try {
      const text = await readFileAsText(file)
      let rows: any[] = []
      if (kind === "csv") rows = parseCSV(text)
      if (kind === "xml") rows = parseXML(text)
      if (kind === "txt") rows = parseTXT(text)
      const items = normalizeToTransactions(rows)
      const res = await fetcher("/api/backup/upload", {
        method: "POST",
        body: { format: kind, transactions: items },
      })
      toast({ title: "Import submitted", description: typeof res === "string" ? res : "Uploaded JSON" })
    } catch (e: any) {
      toast({ title: "Import failed", description: e?.message ?? "Try again later.", variant: "destructive" })
    } finally {
      setLoading(false)
      if (inputRef.current) inputRef.current.value = ""
    }
  }

  async function onExport(kind: "pdf" | "excel") {
    setLoading(true)
    try {
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.pennywise.com"
      const tok = await getIdToken()
      const headers: HeadersInit = {}
      if (tok) headers["Authorization"] = `Bearer ${tok}`
      const res = await fetch(`${base}/api/transactions/export/${kind === "pdf" ? "pdf" : "excel"}`, { headers })
      if (!res.ok) throw new Error(`Failed (${res.status})`)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `pennywise-report.${kind === "pdf" ? "pdf" : "xlsx"}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e: any) {
      const msg = e?.message || "Export failed"
      toast?.({ title: "Export failed", description: msg, variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardContent className="pt-6 space-y-3">
        <div className="flex flex-col md:flex-row items-center gap-3">
          <input ref={inputRef} type="file" accept=".csv,.xml,.txt" className="w-full md:w-auto" />
          <div className="flex gap-2">
            <Button size="sm" onClick={() => onUpload("csv")} disabled={loading}>
              Import CSV
            </Button>
            <Button size="sm" onClick={() => onUpload("xml")} disabled={loading} variant="secondary">
              Import XML
            </Button>
            <Button size="sm" onClick={() => onUpload("txt")} disabled={loading} variant="outline">
              Import TXT
            </Button>
          </div>
          <div className="md:ml-auto flex gap-2">
            <Button size="sm" onClick={() => onExport("pdf")} disabled={loading}>
              Export PDF
            </Button>
            <Button size="sm" variant="secondary" onClick={() => onExport("excel")} disabled={loading}>
              Export Excel
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
