"use client"

import { Pie, PieChart, ResponsiveContainer, Tooltip, Cell, Legend } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useSWR from "swr"
import type { CategorySlice } from "@/lib/types"
import { useAuthedFetcher } from "@/lib/api-client"

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

export function CategoryBreakdownChart() {
  const fetcher = useAuthedFetcher()
  const { data } = useSWR<CategorySlice[]>(["/analytics/categories", {}], ([path, params]) =>
    fetcher(path as string, { params }),
  )

  const slices = data || [
    { category: "Groceries", amount: 320 },
    { category: "Dining", amount: 190 },
    { category: "Transport", amount: 120 },
    { category: "Bills", amount: 260 },
    { category: "Other", amount: 110 },
  ]

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-sm">Category Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={slices} dataKey="amount" nameKey="category" outerRadius={90} innerRadius={50}>
              {slices.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
