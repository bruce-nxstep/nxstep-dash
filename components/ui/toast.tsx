"use client"

import * as React from "react"
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from "lucide-react"
import { cn } from "@/lib/utils"

// ── Types ────────────────────────────────────────────────────────────────────
export type ToastVariant = "success" | "error" | "warning" | "info"

export interface ToastItem {
    id: string
    variant: ToastVariant
    title: string
    description?: string
    duration?: number   // ms, 0 = sticky
}

// ── Singleton state ───────────────────────────────────────────────────────────
type Listener = (toasts: ToastItem[]) => void
let toasts: ToastItem[] = []
const listeners: Set<Listener> = new Set()

const emit = () => listeners.forEach((l) => l([...toasts]))

function addToast(toast: Omit<ToastItem, "id">) {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`
    toasts = [...toasts, { id, duration: 4000, ...toast }]
    emit()
}

function removeToast(id: string) {
    toasts = toasts.filter((t) => t.id !== id)
    emit()
}

// ── Public API (toast.success / toast.error / etc.) ─────────────────────────
export const toast = {
    success: (title: string, description?: string, duration?: number) =>
        addToast({ variant: "success", title, description, duration }),
    error: (title: string, description?: string, duration?: number) =>
        addToast({ variant: "error", title, description, duration }),
    warning: (title: string, description?: string, duration?: number) =>
        addToast({ variant: "warning", title, description, duration }),
    info: (title: string, description?: string, duration?: number) =>
        addToast({ variant: "info", title, description, duration }),
}

// ── Hook ─────────────────────────────────────────────────────────────────────
export function useToast() {
    const [items, setItems] = React.useState<ToastItem[]>([...toasts])
    React.useEffect(() => {
        listeners.add(setItems)
        return () => { listeners.delete(setItems) }
    }, [])
    return { toasts: items, dismiss: removeToast }
}

// ── Single Toast component ────────────────────────────────────────────────────
const ICONS: Record<ToastVariant, React.ReactNode> = {
    success: <CheckCircle2 className="h-4 w-4 text-[var(--color-success)]" />,
    error: <AlertCircle className="h-4 w-4 text-[var(--color-danger)]" />,
    warning: <AlertTriangle className="h-4 w-4 text-[var(--color-warning)]" />,
    info: <Info className="h-4 w-4 text-[var(--color-primary)]" />,
}
const BORDER: Record<ToastVariant, string> = {
    success: "border-l-[var(--color-success)]",
    error: "border-l-[var(--color-danger)]",
    warning: "border-l-[var(--color-warning)]",
    info: "border-l-[var(--color-primary)]",
}

function Toast({ item }: { item: ToastItem }) {
    React.useEffect(() => {
        if (!item.duration) return
        const t = setTimeout(() => removeToast(item.id), item.duration)
        return () => clearTimeout(t)
    }, [item.id, item.duration])

    return (
        <div
            role="alert"
            aria-live="assertive"
            className={cn(
                "flex items-start gap-3 w-80 max-w-full px-4 py-3 rounded-[var(--radius-lg)]",
                "border border-[var(--color-border)] border-l-4 bg-[var(--color-bg-card)] shadow-2xl",
                "animate-in slide-in-from-right-4 fade-in-0 duration-200",
                BORDER[item.variant]
            )}
        >
            <span className="shrink-0 mt-0.5">{ICONS[item.variant]}</span>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-[var(--color-text-primary)]">{item.title}</p>
                {item.description && (
                    <p className="text-xs text-[var(--color-text-muted)] mt-0.5">{item.description}</p>
                )}
            </div>
            <button
                onClick={() => removeToast(item.id)}
                aria-label="Dismiss notification"
                className="shrink-0 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
            >
                <X className="h-3.5 w-3.5" />
            </button>
        </div>
    )
}

// ── Toaster container (place once in layout) ──────────────────────────────────
export function Toaster() {
    const { toasts: items } = useToast()
    if (items.length === 0) return null
    return (
        <div
            aria-label="Notifications"
            className="fixed bottom-4 right-4 z-[200] flex flex-col gap-2 pointer-events-none"
        >
            {items.map((item) => (
                <div key={item.id} className="pointer-events-auto">
                    <Toast item={item} />
                </div>
            ))}
        </div>
    )
}
