"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import type { Transaction } from "@/lib/types"
import { useAuthedFetcher } from "@/lib/api-client"

export function EditTransactionDialog({
  transaction,
  onSaved,
}: {
  transaction: Transaction
  onSaved?: () => void
}) {
  const fetcher = useAuthedFetcher()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({
    ts: transaction.ts,
    merchant: transaction.merchant || "",
    category: transaction.category || "",
    amount: transaction.amount,
    mode: transaction.mode || "",
    remarks: transaction.remarks || "",
    failed: Boolean(transaction.failed),
  })
  const [saving, setSaving] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      await fetcher(`/api/transactions/${transaction.id}`, {
        method: "PUT",
        body: {
          ...form,
          amount: Number(form.amount),
          ts: new Date(form.ts).toISOString(),
        },
      })
      setOpen(false)
      onSaved?.()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          Edit
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Transaction</DialogTitle>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground">Date & Time</label>
              <Input
                type="datetime-local"
                value={toLocalInputValue(form.ts)}
                onChange={(e) => setForm({ ...form, ts: fromLocalInputValue(e.target.value) })}
                required
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Amount</label>
              <Input
                type="number"
                step="0.01"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })}
                required
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Merchant</label>
              <Input value={form.merchant} onChange={(e) => setForm({ ...form, merchant: e.target.value })} />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Category</label>
              <Input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Mode</label>
              <Input value={form.mode} onChange={(e) => setForm({ ...form, mode: e.target.value })} />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Remarks</label>
              <Input value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={form.failed}
                onCheckedChange={(v) => setForm({ ...form, failed: Boolean(v) })}
                id="failed"
              />
              <label htmlFor="failed" className="text-sm">
                Failed
              </label>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function toLocalInputValue(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, "0")
  const yyyy = d.getFullYear()
  const mm = pad(d.getMonth() + 1)
  const dd = pad(d.getDate())
  const hh = pad(d.getHours())
  const min = pad(d.getMinutes())
  return `${yyyy}-${mm}-${dd}T${hh}:${min}`
}
function fromLocalInputValue(val: string) {
  // val like "2025-09-02T10:30"
  const d = new Date(val)
  return d.toISOString()
}
