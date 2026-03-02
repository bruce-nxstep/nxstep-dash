"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight } from "lucide-react"

export interface SidebarItem {
    icon: React.ReactNode
    label: string
    href?: string
    active?: boolean
    badge?: string | number
}

export interface SidebarSection {
    title?: string
    items: SidebarItem[]
}

export interface SidebarProps {
    sections: SidebarSection[]
    bottomSlot?: React.ReactNode
    logo?: React.ReactNode
    defaultCollapsed?: boolean
    className?: string
}

const STORAGE_KEY = "nxstep_sidebar_collapsed"

function Sidebar({ sections, bottomSlot, logo, defaultCollapsed = false, className }: SidebarProps) {
    const [collapsed, setCollapsed] = React.useState(() => {
        if (typeof window === "undefined") return defaultCollapsed
        const stored = localStorage.getItem(STORAGE_KEY)
        return stored !== null ? stored === "true" : defaultCollapsed
    })

    const toggle = () => {
        setCollapsed((c) => {
            const next = !c
            localStorage.setItem(STORAGE_KEY, String(next))
            return next
        })
    }

    return (
        <aside
            className={cn(
                "relative flex flex-col h-full transition-all duration-300 ease-in-out",
                "bg-[var(--color-bg-sidebar)] border-r border-[var(--color-border)]",
                collapsed ? "w-16" : "w-60",
                className
            )}
        >
            {/* Logo */}
            <div className={cn(
                "flex items-center h-14 px-4 border-b border-[var(--color-border)] shrink-0",
                collapsed ? "justify-center" : "justify-between"
            )}>
                {!collapsed && (
                    <div className="text-[var(--color-primary)] font-bold text-base tracking-tight truncate">
                        {logo ?? "◆ NXSTEP"}
                    </div>
                )}
                <button
                    onClick={toggle}
                    aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                    className="p-1.5 rounded-[var(--radius-sm)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-input)] transition-colors shrink-0"
                >
                    {collapsed
                        ? <ChevronRight className="h-4 w-4" />
                        : <ChevronLeft className="h-4 w-4" />
                    }
                </button>
            </div>

            {/* Nav sections */}
            <nav className="flex-1 overflow-y-auto py-3 flex flex-col gap-4" aria-label="Sidebar navigation">
                {sections.map((section, si) => (
                    <div key={si} className="flex flex-col gap-0.5 px-2">
                        {section.title && !collapsed && (
                            <p className="px-2 mb-1 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-muted)]">
                                {section.title}
                            </p>
                        )}
                        {section.items.map((item, ii) => (
                            <a
                                key={ii}
                                href={item.href ?? "#"}
                                aria-current={item.active ? "page" : undefined}
                                title={collapsed ? item.label : undefined}
                                className={cn(
                                    "flex items-center gap-3 px-2 py-2 rounded-[var(--radius-md)] text-sm font-medium transition-colors",
                                    "group relative",
                                    item.active
                                        ? "bg-[var(--color-primary)]/15 text-[var(--color-primary)]"
                                        : "text-[var(--color-text-muted)] hover:bg-[var(--color-bg-input)] hover:text-[var(--color-text-primary)]",
                                    collapsed && "justify-center"
                                )}
                            >
                                <span className="shrink-0 w-5 h-5 flex items-center justify-center">
                                    {item.icon}
                                </span>
                                {!collapsed && (
                                    <span className="truncate flex-1">{item.label}</span>
                                )}
                                {!collapsed && item.badge !== undefined && (
                                    <span className="ml-auto text-[10px] font-bold bg-[var(--color-primary)] text-black rounded-full px-1.5 py-0.5 leading-none">
                                        {item.badge}
                                    </span>
                                )}
                                {/* Tooltip on collapsed */}
                                {collapsed && (
                                    <span className="absolute left-full ml-2 px-2 py-1 rounded-[var(--radius-sm)] bg-[var(--color-bg-card)] border border-[var(--color-border)] text-xs text-[var(--color-text-primary)] whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-lg">
                                        {item.label}
                                        {item.badge !== undefined && ` (${item.badge})`}
                                    </span>
                                )}
                            </a>
                        ))}
                    </div>
                ))}
            </nav>

            {/* Bottom slot */}
            {bottomSlot && (
                <div className={cn(
                    "shrink-0 border-t border-[var(--color-border)] p-3",
                    collapsed && "flex justify-center"
                )}>
                    {bottomSlot}
                </div>
            )}
        </aside>
    )
}

export { Sidebar }
