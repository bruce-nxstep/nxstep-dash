"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface ToggleProps {
    checked?: boolean
    defaultChecked?: boolean
    onChange?: (checked: boolean) => void
    disabled?: boolean
    label?: string
    size?: "sm" | "md"
    className?: string
    id?: string
}

function Toggle({
    checked,
    defaultChecked = false,
    onChange,
    disabled = false,
    label,
    size = "md",
    className,
    id,
}: ToggleProps) {
    const [internal, setInternal] = React.useState(defaultChecked)
    const isControlled = checked !== undefined
    const isOn = isControlled ? checked : internal
    const inputId = id || React.useId()

    const handleChange = () => {
        if (disabled) return
        const next = !isOn
        if (!isControlled) setInternal(next)
        onChange?.(next)
    }

    const trackSize = size === "sm"
        ? "w-8 h-4"
        : "w-11 h-6"
    const thumbSize = size === "sm"
        ? "w-3 h-3"
        : "w-4 h-4"
    const thumbTranslate = size === "sm"
        ? isOn ? "translate-x-4" : "translate-x-0.5"
        : isOn ? "translate-x-5" : "translate-x-1"

    return (
        <label
            htmlFor={inputId}
            className={cn(
                "inline-flex items-center gap-2 cursor-pointer select-none",
                disabled && "cursor-not-allowed opacity-50",
                className
            )}
        >
            <div className="relative" onClick={handleChange}>
                <input
                    id={inputId}
                    type="checkbox"
                    className="sr-only peer"
                    checked={isOn}
                    readOnly
                    disabled={disabled}
                />
                <div
                    className={cn(
                        "rounded-full transition-colors duration-200",
                        trackSize,
                        isOn
                            ? "bg-[var(--color-primary)]"
                            : "bg-[var(--color-border)]"
                    )}
                />
                <div
                    className={cn(
                        "absolute top-1/2 -translate-y-1/2 rounded-full bg-white shadow transition-all duration-200",
                        thumbSize,
                        thumbTranslate
                    )}
                />
            </div>
            {label && (
                <span className="text-sm text-[var(--color-text-primary)]">{label}</span>
            )}
        </label>
    )
}

export { Toggle }
