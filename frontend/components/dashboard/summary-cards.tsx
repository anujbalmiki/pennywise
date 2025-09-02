import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { SummaryResponse } from "@/lib/types"

export function SummaryCards({ data }: { data?: SummaryResponse }) {
  const d = data || {
    weeklySpend: 0,
    monthlySpend: 0,
    totalTransactions: 0,
    failedTransactions: 0,
  }
  return (
    <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <SummaryCard title="Weekly Spend" value={currency(d.weeklySpend)} />
      <SummaryCard title="Monthly Spend" value={currency(d.monthlySpend)} />
      <SummaryCard title="Transactions" value={d.totalTransactions.toLocaleString()} />
      <SummaryCard title="Failed" value={d.failedTransactions.toLocaleString()} />
    </section>
  )
}

function SummaryCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
      </CardContent>
    </Card>
  )
}

function currency(n: number) {
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n)
}
