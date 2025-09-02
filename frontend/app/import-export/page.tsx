"use client"

import { ImportPanel } from "@/components/import-export/import-panel"

export default function ImportExportPage() {
  return (
    <main className="min-h-dvh">
      <div className="mx-auto max-w-6xl px-4 md:px-6 py-6 space-y-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-balance">Import & Export</h1>
          <p className="text-sm text-muted-foreground">Upload bank statements and download reports</p>
        </div>
        <ImportPanel />
      </div>
    </main>
  )
}
