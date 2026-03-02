import * as React from "react"
import { cn } from "@/lib/utils"

export interface ActivityItem {
    id: string
    icon?: React.ReactNode
    title: string
    description?: string
    timestamp: string
    variant?: "default" | "success" | "warning" | "danger"
}

const VARIANT_DOT: Record<string, string> = {
    default: "bg-[var(--color-text-muted)]",
    success: "bg-[var(--color-success)]",
    warning: "bg-[var(--color-warning)]",
    danger: "bg-[var(--color-danger)]",
}

export interface ActivityWidgetProps {
    items: ActivityItem[]
    title?: string
    maxItems?: number
    emptyMessage?: string
    className?: string
}

function ActivityWidget({
    items,
    title = "Recent Activity",
    maxItems = 8,
    emptyMessage = "No recent activity.",
    className,
}: ActivityWidgetProps) {
    const visible = items.slice(0, maxItems)

    return (
        <div
            className={cn(
                "rounded-[var(--radius-xl)] border border-[var(--color-border)]",
                "bg-[var(--color-bg-card)] flex flex-col overflow-hidden",
                className
            )}
        >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--color-border)]">
                <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">{title}</h3>
                {items.length > maxItems && (
                    <span className="text-xs text-[var(--color-text-muted)]">+{items.length - maxItems} more</span>
                )}
            </div>

            {/* Items */}
            <ul className="flex-1 overflow-y-auto divide-y divide-[var(--color-border)]/40">
                {visible.length === 0 ? (
                    <li className="px-5 py-8 text-center text-sm text-[var(--color-text-muted)]">
                        {emptyMessage}
                    </li>
                ) : (
                    visible.map((item) => (
                        <li key={item.id} className="flex items-start gap-3 px-5 py-3.5 hover:bg-[var(--color-bg-input)]/50 transition-colors">
                            {/* Dot or custom icon */}
                            <div className="flex-shrink-0 mt-1.5">
                                {item.icon ?? (
                                    <span className={cn("w-2 h-2 rounded-full block", VARIANT_DOT[item.variant ?? "default"])} />
                                )}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-[var(--color-text-primary)] leading-snug">
                                    {item.title}
                                </p>
                                {item.description && (
                                    <p className="text-xs text-[var(--color-text-muted)] mt-0.5 truncate">
                                        {item.description}
                                    </p>
                                )}
                            </div>
                            <time className="text-[11px] text-[var(--color-text-muted)] shrink-0 mt-0.5 tabular-nums">
                                {item.timestamp}
                            </time>
                        </li>
                    ))
                )}
            </ul>
        </div>
    )
}

export { ActivityWidget }
