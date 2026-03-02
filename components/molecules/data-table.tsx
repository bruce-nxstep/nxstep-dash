"use client"

import * as React from "react"
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"

export interface Column<T> {
    key: keyof T | string
    header: string
    sortable?: boolean
    render?: (row: T) => React.ReactNode
    className?: string
}

export interface DataTableProps<T extends Record<string, unknown>> {
    columns: Column<T>[]
    data: T[]
    rowKey?: keyof T | ((row: T) => string)
    emptyMessage?: string
    className?: string
    pageSize?: number
}

function DataTable<T extends Record<string, unknown>>({
    columns,
    data,
    rowKey,
    emptyMessage = "No data available.",
    className,
    pageSize = 10,
}: DataTableProps<T>) {
    const [sortKey, setSortKey] = React.useState<string | null>(null)
    const [sortDir, setSortDir] = React.useState<"asc" | "desc">("asc")
    const [page, setPage] = React.useState(0)

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"))
        } else {
            setSortKey(key)
            setSortDir("asc")
        }
    }

    const sorted = React.useMemo(() => {
        if (!sortKey) return data
        return [...data].sort((a, b) => {
            const av = a[sortKey] ?? ""
            const bv = b[sortKey] ?? ""
            if (av < bv) return sortDir === "asc" ? -1 : 1
            if (av > bv) return sortDir === "asc" ? 1 : -1
            return 0
        })
    }, [data, sortKey, sortDir])

    const totalPages = Math.ceil(sorted.length / pageSize)
    const paged = sorted.slice(page * pageSize, (page + 1) * pageSize)

    const getKey = (row: T, idx: number): string => {
        if (!rowKey) return String(idx)
        if (typeof rowKey === "function") return rowKey(row)
        return String(row[rowKey as keyof T] ?? idx)
    }

    return (
        <div className={cn("w-full flex flex-col gap-2", className)}>
            <div className="w-full overflow-x-auto rounded-[var(--radius-lg)] border border-[var(--color-border)]">
                <table className="w-full text-sm border-collapse">
                    <thead>
                        <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-input)]">
                            {columns.map((col) => (
                                <th
                                    key={String(col.key)}
                                    scope="col"
                                    className={cn(
                                        "px-4 py-3 text-left font-semibold text-[var(--color-text-muted)] whitespace-nowrap",
                                        col.sortable && "cursor-pointer select-none hover:text-[var(--color-text-primary)] transition-colors",
                                        col.className
                                    )}
                                    onClick={() => col.sortable && handleSort(String(col.key))}
                                >
                                    <span className="flex items-center gap-1.5">
                                        {col.header}
                                        {col.sortable && (
                                            sortKey === String(col.key) ? (
                                                sortDir === "asc"
                                                    ? <ChevronUp className="h-3.5 w-3.5 text-[var(--color-primary)]" />
                                                    : <ChevronDown className="h-3.5 w-3.5 text-[var(--color-primary)]" />
                                            ) : (
                                                <ChevronsUpDown className="h-3.5 w-3.5 opacity-30" />
                                            )
                                        )}
                                    </span>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {paged.length === 0 ? (
                            <tr>
                                <td
                                    colSpan={columns.length}
                                    className="px-4 py-10 text-center text-[var(--color-text-muted)]"
                                >
                                    {emptyMessage}
                                </td>
                            </tr>
                        ) : (
                            paged.map((row, idx) => (
                                <tr
                                    key={getKey(row, idx)}
                                    className="border-b border-[var(--color-border)]/50 last:border-0 hover:bg-[var(--color-primary)]/5 transition-colors"
                                >
                                    {columns.map((col) => (
                                        <td
                                            key={String(col.key)}
                                            className={cn("px-4 py-3 text-[var(--color-text-primary)]", col.className)}
                                        >
                                            {col.render
                                                ? col.render(row)
                                                : String(row[col.key as keyof T] ?? "—")}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)] px-1">
                    <span>
                        {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
                    </span>
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => setPage((p) => Math.max(0, p - 1))}
                            disabled={page === 0}
                            className="px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--color-border)] disabled:opacity-40 hover:border-[var(--color-primary)] transition-colors"
                        >
                            ‹
                        </button>
                        {Array.from({ length: totalPages }).map((_, i) => (
                            <button
                                key={i}
                                onClick={() => setPage(i)}
                                className={cn(
                                    "w-7 h-7 rounded-[var(--radius-sm)] border transition-colors text-xs",
                                    i === page
                                        ? "bg-[var(--color-primary)] text-black border-[var(--color-primary)] font-bold"
                                        : "border-[var(--color-border)] hover:border-[var(--color-primary)]"
                                )}
                            >
                                {i + 1}
                            </button>
                        ))}
                        <button
                            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                            disabled={page === totalPages - 1}
                            className="px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--color-border)] disabled:opacity-40 hover:border-[var(--color-primary)] transition-colors"
                        >
                            ›
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export { DataTable }
