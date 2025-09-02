"use client"

import useSWR from "swr"
import Link from "next/link"
import { useAuth } from "@/components/auth/auth-provider"
import { useAuthedFetcher } from "@/lib/api-client"
import { SummaryCards } from "@/components/dashboard/summary-cards"
import { SpendTrendsChart } from "@/components/dashboard/charts/spend-trends"
import { CategoryBreakdownChart } from "@/components/dashboard/charts/category-breakdown"
import { UserMenu } from "@/components/header/user-menu"
import { ThemeToggle } from "@/components/header/theme-toggle"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  const { user } = useAuth()
  const fetcher = useAuthedFetcher()

  const { data: summary } = useSWR(user ? ["/api/transactions/analytics/summary", {}] : null, ([path, params]) =>
    fetcher(path as string, { params }),
  )

  return (
    <main className="min-h-dvh">
      <header className="border-b">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-balance">Pennywise Dashboard</h1>
          <div className="flex items-center gap-2">
            <Link href="/transactions">
              <Button variant="outline" size="sm">
                Transactions
              </Button>
            </Link>
            <Link href="/import-export">
              <Button variant="outline" size="sm">
                Import/Export
              </Button>
            </Link>
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-6 space-y-8">
        <SummaryCards data={summary} />
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SpendTrendsChart />
          <CategoryBreakdownChart />
        </section>
      </div>
    </main>
  )
}
