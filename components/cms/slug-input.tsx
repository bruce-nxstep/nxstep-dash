"use client"

import * as React from "react"
import { Globe, Pencil, Lock } from "lucide-react"
import { cn } from "@/lib/utils"

export interface SlugInputProps {
    value?: string
    onChange?: (slug: string) => void
    prefix?: string
    sourceValue?: string   // title to auto-generate from
    disabled?: boolean
    className?: string
}

function toSlug(str: string): string {
    return str
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9\s-]/g, "")
        .trim()
        .replace(/[\s_]+/g, "-")
        .replace(/-+/g, "-")
}

function SlugInput({
    value,
    onChange,
    prefix = "/blog/",
    sourceValue,
    disabled = false,
    className,
}: SlugInputProps) {
    const [locked, setLocked] = React.useState(true)
    const [internal, setInternal] = React.useState(value ?? "")

    // Auto-generate slug from source when locked
    React.useEffect(() => {
        if (locked && sourceValue !== undefined) {
            const generated = toSlug(sourceValue)
            setInternal(generated)
            onChange?.(generated)
        }
    }, [sourceValue, locked])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const raw = toSlug(e.target.value)
        setInternal(raw)
        onChange?.(raw)
    }

    return (
        <div className={cn("flex flex-col gap-1", className)}>
            <div
                className={cn(
                    "flex items-center rounded-[var(--radius-md)] border overflow-hidden transition-colors",
                    "bg-[var(--color-bg-input)]",
                    disabled ? "border-[var(--color-border)] opacity-50" : "border-[var(--color-border)]",
                    !locked && "border-[var(--color-primary)]/50"
                )}
            >
                {/* Globe icon */}
                <span className="pl-3 pr-1 text-[var(--color-text-muted)]">
                    <Globe className="h-3.5 w-3.5" />
                </span>
                {/* Prefix */}
                <span className="pr-0 text-sm text-[var(--color-text-muted)] whitespace-nowrap select-none">
                    {prefix}
                </span>
                {/* Slug input */}
                <input
                    type="text"
                    value={internal}
                    onChange={handleChange}
                    disabled={locked || disabled}
                    placeholder="auto-generated"
                    className={cn(
                        "flex-1 min-w-0 pr-2 py-2 text-sm bg-transparent outline-none",
                        "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
                        (locked || disabled) && "cursor-not-allowed"
                    )}
                />
                {/* Lock/unlock toggle */}
                {!disabled && (
                    <button
                        type="button"
                        onClick={() => setLocked((l) => !l)}
                        aria-label={locked ? "Unlock slug to edit" : "Lock slug"}
                        title={locked ? "Click to edit manually" : "Click to auto-generate"}
                        className="px-3 py-2 text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors border-l border-[var(--color-border)]"
                    >
                        {locked ? <Lock className="h-3.5 w-3.5" /> : <Pencil className="h-3.5 w-3.5" />}
                    </button>
                )}
            </div>
            <p className="text-[11px] text-[var(--color-text-muted)]">
                {locked ? "Auto-generated from title. Click 🔒 to override." : "Editing manually. Only lowercase, numbers and hyphens."}
            </p>
        </div>
    )
}

export { SlugInput, toSlug }
