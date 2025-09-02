"use client"

import { TransactionsTable } from "@/components/transactions/transactions-table"

export default function TransactionsPage() {
  return (
    <main className="min-h-dvh">
      <div className="mx-auto max-w-6xl px-4 md:px-6 py-6 space-y-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-balance">Transactions</h1>
          <p className="text-sm text-muted-foreground">Search, filter, and edit your transactions</p>
        </div>
        <TransactionsTable />
      </div>
    </main>
  )
}
