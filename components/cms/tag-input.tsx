"use client"

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

export interface TagInputProps {
    tags?: string[]
    defaultTags?: string[]
    onChange?: (tags: string[]) => void
    placeholder?: string
    maxTags?: number
    disabled?: boolean
    className?: string
}

function TagInput({
    tags,
    defaultTags = [],
    onChange,
    placeholder = "Add tag…",
    maxTags = 20,
    disabled = false,
    className,
}: TagInputProps) {
    const isControlled = tags !== undefined
    const [internal, setInternal] = React.useState<string[]>(defaultTags)
    const current = isControlled ? tags : internal
    const [input, setInput] = React.useState("")
    const inputRef = React.useRef<HTMLInputElement>(null)

    const addTag = (raw: string) => {
        const tag = raw.trim().toLowerCase()
        if (!tag || current.includes(tag) || current.length >= maxTags) return
        const next = [...current, tag]
        if (!isControlled) setInternal(next)
        onChange?.(next)
        setInput("")
    }

    const removeTag = (tag: string) => {
        const next = current.filter((t) => t !== tag)
        if (!isControlled) setInternal(next)
        onChange?.(next)
    }

    const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" || e.key === ",") {
            e.preventDefault()
            addTag(input)
        } else if (e.key === "Backspace" && input === "" && current.length > 0) {
            removeTag(current[current.length - 1])
        }
    }

    return (
        <div
            className={cn(
                "flex flex-wrap gap-1.5 items-center p-2 rounded-[var(--radius-md)]",
                "bg-[var(--color-bg-input)] border border-[var(--color-border)] cursor-text",
                "transition-colors focus-within:border-[var(--color-primary)]/60 focus-within:ring-2 focus-within:ring-[var(--color-primary)]/20",
                disabled && "opacity-50 cursor-not-allowed",
                className
            )}
            onClick={() => inputRef.current?.focus()}
        >
            {/* Tags */}
            {current.map((tag) => (
                <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--color-primary)]/20 text-[var(--color-primary)] border border-[var(--color-primary)]/30"
                >
                    {tag}
                    {!disabled && (
                        <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); removeTag(tag) }}
                            aria-label={`Remove tag ${tag}`}
                            className="hover:text-[var(--color-danger)] transition-colors"
                        >
                            <X className="h-2.5 w-2.5" />
                        </button>
                    )}
                </span>
            ))}

            {/* Input */}
            {current.length < maxTags && !disabled && (
                <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKey}
                    onBlur={() => input && addTag(input)}
                    placeholder={current.length === 0 ? placeholder : ""}
                    className="flex-1 min-w-[80px] bg-transparent outline-none text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]"
                />
            )}

            {/* Max indicator */}
            {current.length >= maxTags && (
                <span className="text-xs text-[var(--color-text-muted)]">Max {maxTags}</span>
            )}
        </div>
    )
}

export { TagInput }
