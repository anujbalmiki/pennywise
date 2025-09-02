import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { SWRConfig } from "swr"
import { AuthProvider } from "@/components/auth/auth-provider"
import { Suspense } from "react"
import { ThemeProvider } from "@/components/theme-provider"
import Navbar from "@/components/header/navbar"
import "./globals.css"

export const metadata: Metadata = {
  title: "v0 App",
  description: "Created with v0",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`font-sans ${GeistSans.variable} ${GeistMono.variable} antialiased bg-background text-foreground min-h-dvh`}
      >
        <SWRConfig
          value={{
            provider: () => new Map(),
            // Note: we attach fetchers per-hook to inject the Firebase token dynamically
            revalidateOnFocus: true,
            dedupingInterval: 2000,
          }}
        >
          <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
            <Suspense fallback={null}>
              <AuthProvider>
                <Navbar />
                {children}
              </AuthProvider>
            </Suspense>
          </ThemeProvider>
        </SWRConfig>
        <Analytics />
      </body>
    </html>
  )
}
