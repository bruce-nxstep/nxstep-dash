import * as React from "react"
import { ChevronRight, Home } from "lucide-react"
import { cn } from "@/lib/utils"

export interface BreadcrumbItem {
    label: string
    href?: string
    icon?: React.ReactNode
}

export interface BreadcrumbProps {
    items: BreadcrumbItem[]
    homeIcon?: boolean
    className?: string
}

function Breadcrumb({ items, homeIcon = true, className }: BreadcrumbProps) {
    return (
        <nav aria-label="Breadcrumb" className={cn("flex items-center", className)}>
            <ol className="flex items-center gap-1 flex-wrap">
                {items.map((item, idx) => {
                    const isLast = idx === items.length - 1
                    return (
                        <li key={idx} className="flex items-center gap-1">
                            {idx === 0 && homeIcon && (
                                <Home className="h-3.5 w-3.5 text-[var(--color-text-muted)] mr-0.5" />
                            )}
                            {isLast ? (
                                <span
                                    aria-current="page"
                                    className="text-sm text-[var(--color-text-primary)] font-medium"
                                >
                                    {item.label}
                                </span>
                            ) : (
                                <a
                                    href={item.href ?? "#"}
                                    className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors"
                                >
                                    {item.label}
                                </a>
                            )}
                            {!isLast && (
                                <ChevronRight className="h-3.5 w-3.5 text-[var(--color-border)] flex-shrink-0" />
                            )}
                        </li>
                    )
                })}
            </ol>
        </nav>
    )
}

export { Breadcrumb }
