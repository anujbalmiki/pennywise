"use client"

import useSWR from "swr"
import { useAuth } from "@/components/auth/auth-provider"
import { LoginCard } from "@/components/auth/login-card"
import { useAuthedFetcher } from "@/lib/api-client"
import { SummaryCards } from "@/components/dashboard/summary-cards"
import { SpendTrendsChart } from "@/components/dashboard/charts/spend-trends"
import { CategoryBreakdownChart } from "@/components/dashboard/charts/category-breakdown"

export default function HomePage() {
  const { user, loading } = useAuth()
  const fetcher = useAuthedFetcher()

  const { data: summary } = useSWR(user ? ["/api/transactions/analytics/summary", {}] : null, ([path, params]) =>
    fetcher(path as string, { params }),
  )

  if (loading) {
    return (
      <main className="min-h-dvh flex items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </main>
    )
  }

  if (!user) {
    return (
      <main className="min-h-dvh flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <LoginCard />
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-dvh">
      <div className="mx-auto max-w-6xl px-4 md:px-6 py-6 space-y-8">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-balance">Overview</h1>
            <p className="text-sm text-muted-foreground">Spending summary and insights</p>
          </div>
        </div>

        <SummaryCards data={summary} />
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SpendTrendsChart />
          <CategoryBreakdownChart />
        </section>
      </div>
    </main>
  )
}
