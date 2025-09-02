"use client"

import type React from "react"

import { useState } from "react"
import useSWR from "swr"
import { useAuthedFetcher } from "@/lib/api-client"
import type { Transaction } from "@/lib/types"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { EditTransactionDialog } from "./edit-transaction-dialog"

export function TransactionsTable() {
  const fetcher = useAuthedFetcher()
  const [q, setQ] = useState({
    start: "",
    end: "",
    merchant: "",
    category: "",
    mode: "",
    remarks: "",
    failedOnly: false,
  })

  const { data, isLoading, mutate } = useSWR<Transaction[]>(["/api/transactions", { ...q }], ([path, params]) =>
    fetcher(path as string, { params }),
  )

  const visible = data || []

  return (
    <Card>
      <CardContent className="pt-6 space-y-4">
        <Filters
          q={q}
          onChange={setQ}
          onApply={() => mutate()}
          onReset={() =>
            setQ({ start: "", end: "", merchant: "", category: "", mode: "", remarks: "", failedOnly: false })
          }
        />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left bg-muted/50">
              <tr>
                <Th>Date</Th>
                <Th>Merchant</Th>
                <Th>Category</Th>
                <Th className="text-right">Amount</Th>
                <Th>Mode</Th>
                <Th>Remarks</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td className="py-6 text-center text-muted-foreground" colSpan={8}>
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && visible.length === 0 && (
                <tr>
                  <td className="py-6 text-center text-muted-foreground" colSpan={8}>
                    No transactions found
                  </td>
                </tr>
              )}
              {visible.map((t) => (
                <tr key={t.id} className="border-t">
                  <Td>{new Date(t.ts).toLocaleString()}</Td>
                  <Td>{t.merchant || "-"}</Td>
                  <Td>{t.category || "-"}</Td>
                  <Td className="text-right font-medium">{currency(t.amount)}</Td>
                  <Td>{t.mode || "-"}</Td>
                  <Td>{t.remarks || "-"}</Td>
                  <Td>
                    {t.failed ? (
                      <span className="text-xs px-2 py-1 rounded bg-destructive/10 text-destructive">Failed</span>
                    ) : (
                      <span className="text-xs px-2 py-1 rounded bg-secondary text-secondary-foreground">OK</span>
                    )}
                  </Td>
                  <Td>
                    <EditTransactionDialog transaction={t} onSaved={() => mutate()} />
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

function Filters({
  q,
  onChange,
  onApply,
  onReset,
}: {
  q: {
    start: string
    end: string
    merchant: string
    category: string
    mode: string
    remarks: string
    failedOnly: boolean
  }
  onChange: (v: any) => void
  onApply: () => void
  onReset: () => void
}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
      <Input type="date" value={q.start} onChange={(e) => onChange({ ...q, start: e.target.value })} />
      <Input type="date" value={q.end} onChange={(e) => onChange({ ...q, end: e.target.value })} />
      <Input placeholder="Merchant" value={q.merchant} onChange={(e) => onChange({ ...q, merchant: e.target.value })} />
      <Input placeholder="Category" value={q.category} onChange={(e) => onChange({ ...q, category: e.target.value })} />
      <Input placeholder="Mode" value={q.mode} onChange={(e) => onChange({ ...q, mode: e.target.value })} />
      <Input placeholder="Remarks" value={q.remarks} onChange={(e) => onChange({ ...q, remarks: e.target.value })} />
      <div className="flex items-center gap-2 col-span-2 md:col-span-6">
        <label className="flex items-center gap-2 text-sm">
          <Checkbox checked={q.failedOnly} onCheckedChange={(v) => onChange({ ...q, failedOnly: Boolean(v) })} />
          Failed only
        </label>
        <div className="ml-auto flex gap-2">
          <Button variant="secondary" onClick={onReset}>
            Reset
          </Button>
          <Button onClick={onApply}>Apply</Button>
        </div>
      </div>
    </div>
  )
}

function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <th className={`py-2 px-3 text-xs font-medium ${className}`}>{children}</th>
}
function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`py-2 px-3 ${className}`}>{children}</td>
}
function currency(n: number) {
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(n)
}
