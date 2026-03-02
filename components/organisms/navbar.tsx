"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Menu, X } from "lucide-react"

export interface NavLink {
    label: string
    href: string
    active?: boolean
}

export interface NavbarProps {
    logo?: React.ReactNode
    links?: NavLink[]
    cta?: React.ReactNode
    userSlot?: React.ReactNode
    className?: string
}

function Navbar({ logo, links = [], cta, userSlot, className }: NavbarProps) {
    const [mobileOpen, setMobileOpen] = React.useState(false)

    return (
        <header
            className={cn(
                "w-full border-b border-[var(--color-border)]",
                "bg-[var(--color-bg-sidebar)]/80 backdrop-blur-lg",
                "sticky top-0 z-40",
                className
            )}
        >
            <nav
                aria-label="Main navigation"
                className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-6"
            >
                {/* Logo */}
                <div className="flex-shrink-0 text-[var(--color-primary)] font-bold text-lg tracking-tight">
                    {logo ?? "NXSTEP"}
                </div>

                {/* Desktop links */}
                <ul className="hidden md:flex items-center gap-6 flex-1">
                    {links.map((link) => (
                        <li key={link.href}>
                            <a
                                href={link.href}
                                aria-current={link.active ? "page" : undefined}
                                className={cn(
                                    "text-sm font-medium transition-colors",
                                    link.active
                                        ? "text-[var(--color-primary)]"
                                        : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
                                )}
                            >
                                {link.label}
                            </a>
                        </li>
                    ))}
                </ul>

                {/* Right slot */}
                <div className="hidden md:flex items-center gap-3">
                    {userSlot}
                    {cta}
                </div>

                {/* Mobile hamburger */}
                <button
                    className="md:hidden text-[var(--color-text-muted)]"
                    onClick={() => setMobileOpen((o) => !o)}
                    aria-label={mobileOpen ? "Close menu" : "Open menu"}
                    aria-expanded={mobileOpen}
                >
                    {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
            </nav>

            {/* Mobile drawer */}
            {mobileOpen && (
                <div className="md:hidden border-t border-[var(--color-border)] bg-[var(--color-bg-card)] px-4 py-3 flex flex-col gap-3">
                    {links.map((link) => (
                        <a
                            key={link.href}
                            href={link.href}
                            aria-current={link.active ? "page" : undefined}
                            className={cn(
                                "text-sm py-1.5 font-medium transition-colors",
                                link.active
                                    ? "text-[var(--color-primary)]"
                                    : "text-[var(--color-text-muted)]"
                            )}
                            onClick={() => setMobileOpen(false)}
                        >
                            {link.label}
                        </a>
                    ))}
                    {cta && <div className="pt-1">{cta}</div>}
                </div>
            )}
        </header>
    )
}

export { Navbar }
