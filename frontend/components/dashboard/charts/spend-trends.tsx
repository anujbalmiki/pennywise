"use client"

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useSWR from "swr"
import type { TrendPoint } from "@/lib/types"
import { useAuthedFetcher } from "@/lib/api-client"

export function SpendTrendsChart() {
  const fetcher = useAuthedFetcher()
  const { data } = useSWR<TrendPoint[]>(["/analytics/trends", {}], ([path, params]) =>
    fetcher(path as string, { params }),
  )

  const points =
    data ||
    Array.from({ length: 12 }).map((_, i) => ({
      date: `W${i + 1}`,
      amount: Math.round(200 + Math.random() * 800),
    }))

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-sm">Cash Flow (Weekly)</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="amount" stroke="hsl(var(--chart-1))" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
