"use client"

import * as React from "react"
import { Bell, Search, ChevronDown, Settings, User, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import { Avatar } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

export interface TopbarUser {
    name: string
    email?: string
    avatar?: string
    initials?: string
}

export interface TopbarProps {
    user?: TopbarUser
    notificationCount?: number
    onSearch?: (query: string) => void
    breadcrumbSlot?: React.ReactNode
    actionsSlot?: React.ReactNode
    className?: string
}

function Topbar({
    user,
    notificationCount = 0,
    onSearch,
    breadcrumbSlot,
    actionsSlot,
    className,
}: TopbarProps) {
    const [query, setQuery] = React.useState("")
    const [userMenuOpen, setUserMenuOpen] = React.useState(false)
    const userMenuRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
                setUserMenuOpen(false)
            }
        }
        document.addEventListener("mousedown", handler)
        return () => document.removeEventListener("mousedown", handler)
    }, [])

    return (
        <header
            className={cn(
                "h-14 w-full flex items-center gap-4 px-4 shrink-0",
                "bg-[var(--color-bg-sidebar)]/80 backdrop-blur-lg",
                "border-b border-[var(--color-border)] sticky top-0 z-30",
                className
            )}
        >
            {/* Breadcrumb slot */}
            {breadcrumbSlot && (
                <div className="hidden md:flex items-center flex-1 min-w-0">
                    {breadcrumbSlot}
                </div>
            )}

            {/* Global search */}
            <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--color-text-muted)] pointer-events-none" />
                <input
                    type="search"
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value)
                        onSearch?.(e.target.value)
                    }}
                    placeholder="Search…"
                    className={cn(
                        "w-full pl-8 pr-3 py-1.5 text-sm rounded-[var(--radius-md)]",
                        "bg-[var(--color-bg-input)] border border-[var(--color-border)]",
                        "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
                        "outline-none focus:border-[var(--color-primary)]/60 focus:ring-2 focus:ring-[var(--color-primary)]/20",
                        "transition-all [&::-webkit-search-cancel-button]:hidden"
                    )}
                />
                <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-[var(--color-text-muted)] bg-[var(--color-bg-app)] border border-[var(--color-border)] px-1.5 py-0.5 rounded hidden sm:inline-flex">
                    ⌘K
                </kbd>
            </div>

            <div className="flex items-center gap-2 ml-auto shrink-0">
                {actionsSlot}

                {/* Notifications */}
                <button
                    aria-label={`${notificationCount} notifications`}
                    className="relative p-2 rounded-[var(--radius-md)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-input)] transition-colors"
                >
                    <Bell className="h-4 w-4" />
                    {notificationCount > 0 && (
                        <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[var(--color-danger)]" />
                    )}
                </button>

                {/* User menu */}
                {user && (
                    <div ref={userMenuRef} className="relative">
                        <button
                            onClick={() => setUserMenuOpen((o) => !o)}
                            aria-expanded={userMenuOpen}
                            aria-haspopup="menu"
                            className="flex items-center gap-2 p-1 pr-2 rounded-[var(--radius-md)] hover:bg-[var(--color-bg-input)] transition-colors"
                        >
                            <Avatar
                                src={user.avatar}
                                initials={user.initials ?? user.name.slice(0, 2).toUpperCase()}
                                size="sm"
                            />
                            <span className="hidden md:block text-sm font-medium text-[var(--color-text-primary)] max-w-[120px] truncate">
                                {user.name}
                            </span>
                            <ChevronDown className={cn("h-3.5 w-3.5 text-[var(--color-text-muted)] transition-transform", userMenuOpen && "rotate-180")} />
                        </button>

                        {userMenuOpen && (
                            <div
                                role="menu"
                                className={cn(
                                    "absolute right-0 mt-1 w-52 rounded-[var(--radius-lg)] border border-[var(--color-border)]",
                                    "bg-[var(--color-bg-card)] shadow-2xl py-1 z-50"
                                )}
                            >
                                <div className="px-3 py-2 border-b border-[var(--color-border)]">
                                    <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">{user.name}</p>
                                    {user.email && <p className="text-xs text-[var(--color-text-muted)] truncate">{user.email}</p>}
                                </div>
                                {[
                                    { icon: <User className="h-4 w-4" />, label: "Profile" },
                                    { icon: <Settings className="h-4 w-4" />, label: "Settings" },
                                    { icon: <LogOut className="h-4 w-4" />, label: "Log out", danger: true },
                                ].map((item) => (
                                    <button
                                        key={item.label}
                                        role="menuitem"
                                        className={cn(
                                            "w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors",
                                            item.danger
                                                ? "text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10"
                                                : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-input)] hover:text-[var(--color-text-primary)]"
                                        )}
                                    >
                                        {item.icon} {item.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </header>
    )
}

export { Topbar }
