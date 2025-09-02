"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { Menu, LineChart, Table, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import { ThemeToggle } from "./theme-toggle"
import { UserMenu } from "./user-menu"

const navItems = [
  { href: "/", label: "Home", icon: LineChart },
  { href: "/transactions", label: "Transactions", icon: Table },
  { href: "/import-export", label: "Import & Export", icon: Upload },
]

function NavLinks({ onNavigate, className }: { onNavigate?: () => void; className?: string }) {
  const pathname = usePathname()
  return (
    <ul className={cn("flex items-center gap-2", className)}>
      {navItems.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || (href !== "/" && pathname.startsWith(href))
        return (
          <li key={href}>
            <Link
              href={href}
              onClick={onNavigate}
              className={cn(
                "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors w-full md:w-auto justify-start",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-foreground/80 hover:text-foreground hover:bg-muted",
              )}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              <span className="text-pretty whitespace-nowrap">{label}</span>
            </Link>
          </li>
        )
      })}
    </ul>
  )
}

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-3">
          {/* Mobile menu */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" aria-label="Open menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 max-w-[85vw]">
              <SheetHeader>
                <SheetTitle>Pennywise</SheetTitle>
              </SheetHeader>
              <nav className="mt-4">
                <NavLinks onNavigate={() => setOpen(false)} className="flex-col items-stretch gap-1" />
              </nav>
            </SheetContent>
          </Sheet>

          {/* Brand */}
          <Link href="/" className="flex items-center gap-2">
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground font-semibold">
              P
            </span>
            <span className="text-sm font-semibold tracking-tight text-foreground text-balance">Pennywise</span>
          </Link>

          {/* Desktop nav */}
          <nav className="ml-2 hidden md:block">
            <NavLinks />
          </nav>
        </div>

        <div className="flex items-center gap-1">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  )
}
