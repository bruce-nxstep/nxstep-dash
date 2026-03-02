"use client"

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

type ModalSize = "sm" | "md" | "lg" | "full"

const SIZE_CLASSES: Record<ModalSize, string> = {
    sm: "max-w-sm",
    md: "max-w-lg",
    lg: "max-w-2xl",
    full: "max-w-[95vw] h-[95vh]",
}

export interface ModalProps {
    open: boolean
    onClose: () => void
    title?: React.ReactNode
    size?: ModalSize
    hideCloseButton?: boolean
    className?: string
    children: React.ReactNode
    footer?: React.ReactNode
}

function Modal({
    open,
    onClose,
    title,
    size = "md",
    hideCloseButton = false,
    className,
    children,
    footer,
}: ModalProps) {
    // Lock scroll when open
    React.useEffect(() => {
        if (open) document.body.style.overflow = "hidden"
        return () => { document.body.style.overflow = "" }
    }, [open])

    // Close on Escape
    React.useEffect(() => {
        const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
        if (open) document.addEventListener("keydown", handler)
        return () => document.removeEventListener("keydown", handler)
    }, [open, onClose])

    if (!open) return null

    return (
        <div
            role="dialog"
            aria-modal="true"
            aria-label={typeof title === "string" ? title : "Modal"}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        >
            {/* Overlay */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* Panel */}
            <div
                className={cn(
                    "relative z-10 w-full flex flex-col",
                    "rounded-[var(--radius-xl)] border border-[var(--color-border)]",
                    "bg-[var(--color-bg-card)] shadow-2xl",
                    SIZE_CLASSES[size],
                    size === "full" ? "overflow-hidden" : "max-h-[90vh]",
                    className
                )}
            >
                {/* Header */}
                {(title || !hideCloseButton) && (
                    <div className="flex items-center justify-between gap-4 px-6 py-4 border-b border-[var(--color-border)]">
                        {title && (
                            <h2 className="text-base font-semibold text-[var(--color-text-primary)]">
                                {title}
                            </h2>
                        )}
                        {!hideCloseButton && (
                            <button
                                onClick={onClose}
                                aria-label="Close modal"
                                className="ml-auto text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors rounded-[var(--radius-sm)] p-1"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                )}

                {/* Body */}
                <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>

                {/* Footer */}
                {footer && (
                    <div className="px-6 py-4 border-t border-[var(--color-border)] flex items-center justify-end gap-2">
                        {footer}
                    </div>
                )}
            </div>
        </div>
    )
}

export { Modal }
