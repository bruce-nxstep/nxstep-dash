"use client"

import * as React from "react"
import { Send, FileEdit, Trash2, Clock, CheckCircle2, Circle } from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

export type ContentStatus = "draft" | "published" | "scheduled"

const STATUS_CONFIG: Record<ContentStatus, { label: string; variant: "default" | "success" | "warning" }> = {
    draft: { label: "Draft", variant: "default" },
    published: { label: "Published", variant: "success" },
    scheduled: { label: "Scheduled", variant: "warning" },
}

export interface ContentToolbarProps {
    status?: ContentStatus
    onPublish?: () => void
    onDraft?: () => void
    onSchedule?: () => void
    onDelete?: () => void
    lastSaved?: string      // e.g. "2 min ago"
    saving?: boolean
    className?: string
}

function ContentToolbar({
    status = "draft",
    onPublish,
    onDraft,
    onSchedule,
    onDelete,
    lastSaved,
    saving = false,
    className,
}: ContentToolbarProps) {
    const cfg = STATUS_CONFIG[status]

    return (
        <div
            className={cn(
                "flex items-center flex-wrap gap-3 px-4 py-3",
                "rounded-[var(--radius-xl)] border border-[var(--color-border)]",
                "bg-[var(--color-bg-card)]",
                className
            )}
        >
            {/* Status badge */}
            <Badge variant={cfg.variant} size="md">{cfg.label}</Badge>

            {/* Save indicator */}
            <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)]">
                {saving
                    ? <><Circle className="h-3 w-3 animate-spin" /> Saving…</>
                    : lastSaved
                        ? <><CheckCircle2 className="h-3 w-3 text-[var(--color-success)]" /> Saved {lastSaved}</>
                        : null
                }
            </div>

            {/* Actions — push to right */}
            <div className="ml-auto flex items-center gap-2">
                {onDraft && status !== "draft" && (
                    <button
                        onClick={onDraft}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-medium text-[var(--color-text-muted)] hover:bg-[var(--color-bg-input)] border border-[var(--color-border)] transition-colors"
                    >
                        <FileEdit className="h-3.5 w-3.5" />
                        Set Draft
                    </button>
                )}
                {onSchedule && status !== "scheduled" && (
                    <button
                        onClick={onSchedule}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-medium text-[var(--color-text-muted)] hover:bg-[var(--color-bg-input)] border border-[var(--color-border)] transition-colors"
                    >
                        <Clock className="h-3.5 w-3.5" />
                        Schedule
                    </button>
                )}
                {onPublish && status !== "published" && (
                    <button
                        onClick={onPublish}
                        className="flex items-center gap-1.5 px-4 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-black bg-[var(--color-primary)] hover:bg-[var(--color-primary-light)] transition-colors"
                    >
                        <Send className="h-3.5 w-3.5" />
                        Publish
                    </button>
                )}
                {onDelete && (
                    <button
                        onClick={onDelete}
                        className="flex items-center gap-1 px-2 py-1.5 rounded-[var(--radius-md)] text-xs font-medium text-[var(--color-danger)] hover:bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/30 transition-colors"
                    >
                        <Trash2 className="h-3.5 w-3.5" />
                    </button>
                )}
            </div>
        </div>
    )
}

export { ContentToolbar }
