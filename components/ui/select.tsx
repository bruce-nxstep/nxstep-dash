"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown, Check } from "lucide-react"

export interface SelectOption {
    value: string
    label: string
    disabled?: boolean
}

export interface SelectProps {
    options: SelectOption[]
    value?: string
    defaultValue?: string
    onChange?: (value: string) => void
    placeholder?: string
    disabled?: boolean
    className?: string
    id?: string
}

function Select({
    options,
    value,
    defaultValue,
    onChange,
    placeholder = "Select an option",
    disabled = false,
    className,
    id,
}: SelectProps) {
    const [open, setOpen] = React.useState(false)
    const [internal, setInternal] = React.useState(defaultValue ?? "")
    const isControlled = value !== undefined
    const selected = isControlled ? value : internal
    const inputId = id || React.useId()
    const ref = React.useRef<HTMLDivElement>(null)
    const selectedLabel = options.find((o) => o.value === selected)?.label

    // Close on outside click
    React.useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
        }
        document.addEventListener("mousedown", handler)
        return () => document.removeEventListener("mousedown", handler)
    }, [])

    const choose = (opt: SelectOption) => {
        if (opt.disabled) return
        if (!isControlled) setInternal(opt.value)
        onChange?.(opt.value)
        setOpen(false)
    }

    return (
        <div ref={ref} className={cn("relative w-full", className)}>
            <button
                id={inputId}
                type="button"
                disabled={disabled}
                onClick={() => !disabled && setOpen((o) => !o)}
                aria-haspopup="listbox"
                aria-expanded={open}
                className={cn(
                    "w-full flex items-center justify-between gap-2 px-3 py-2 rounded-[var(--radius-md)]",
                    "bg-[var(--color-bg-input)] border border-[var(--color-border)]",
                    "text-sm text-left transition-all",
                    selected ? "text-[var(--color-text-primary)]" : "text-[var(--color-text-muted)]",
                    "hover:border-[var(--color-primary)]/50",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]/50",
                    open && "border-[var(--color-primary)]/60",
                    disabled && "opacity-50 cursor-not-allowed"
                )}
            >
                <span>{selectedLabel ?? placeholder}</span>
                <ChevronDown
                    className={cn("h-4 w-4 text-[var(--color-text-muted)] transition-transform", open && "rotate-180")}
                />
            </button>

            {open && (
                <ul
                    role="listbox"
                    className={cn(
                        "absolute z-50 mt-1 w-full rounded-[var(--radius-md)] border border-[var(--color-border)]",
                        "bg-[var(--color-bg-card)] shadow-xl py-1 max-h-60 overflow-auto"
                    )}
                >
                    {options.map((opt) => (
                        <li
                            key={opt.value}
                            role="option"
                            aria-selected={selected === opt.value}
                            onClick={() => choose(opt)}
                            className={cn(
                                "flex items-center justify-between px-3 py-2 text-sm cursor-pointer transition-colors",
                                opt.disabled
                                    ? "text-[var(--color-text-muted)] cursor-not-allowed opacity-50"
                                    : "text-[var(--color-text-primary)] hover:bg-[var(--color-primary)]/10",
                                selected === opt.value && "text-[var(--color-primary)] font-medium"
                            )}
                        >
                            {opt.label}
                            {selected === opt.value && <Check className="h-3.5 w-3.5" />}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}

export { Select }
