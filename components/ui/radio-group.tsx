"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface RadioOption {
    value: string
    label: string
    description?: string
    disabled?: boolean
}

export interface RadioGroupProps {
    options: RadioOption[]
    value?: string
    defaultValue?: string
    onChange?: (value: string) => void
    name?: string
    orientation?: "vertical" | "horizontal"
    className?: string
}

function RadioGroup({
    options,
    value,
    defaultValue,
    onChange,
    name,
    orientation = "vertical",
    className,
}: RadioGroupProps) {
    const [internal, setInternal] = React.useState(defaultValue ?? "")
    const isControlled = value !== undefined
    const selected = isControlled ? value : internal
    const groupName = name || React.useId()

    return (
        <div
            role="radiogroup"
            className={cn(
                "flex gap-3",
                orientation === "vertical" ? "flex-col" : "flex-row flex-wrap",
                className
            )}
        >
            {options.map((opt) => {
                const isSelected = selected === opt.value
                const radioId = `${groupName}-${opt.value}`

                return (
                    <label
                        key={opt.value}
                        htmlFor={radioId}
                        className={cn(
                            "flex items-start gap-2.5 cursor-pointer select-none",
                            opt.disabled && "cursor-not-allowed opacity-50"
                        )}
                    >
                        <span className="relative flex-shrink-0 mt-0.5">
                            <input
                                id={radioId}
                                type="radio"
                                name={groupName}
                                value={opt.value}
                                checked={isSelected}
                                disabled={opt.disabled}
                                className="sr-only peer"
                                onChange={() => {
                                    if (opt.disabled) return
                                    if (!isControlled) setInternal(opt.value)
                                    onChange?.(opt.value)
                                }}
                            />
                            {/* Outer ring */}
                            <span
                                className={cn(
                                    "w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all",
                                    isSelected
                                        ? "border-[var(--color-primary)]"
                                        : "border-[var(--color-border)]",
                                    "peer-focus-visible:ring-2 peer-focus-visible:ring-[var(--color-primary)]/50 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-[var(--color-bg-app)]"
                                )}
                            >
                                {isSelected && (
                                    <span className="w-2 h-2 rounded-full bg-[var(--color-primary)]" />
                                )}
                            </span>
                        </span>
                        <span className="flex flex-col">
                            <span className="text-sm font-medium text-[var(--color-text-primary)]">
                                {opt.label}
                            </span>
                            {opt.description && (
                                <span className="text-xs text-[var(--color-text-muted)]">
                                    {opt.description}
                                </span>
                            )}
                        </span>
                    </label>
                )
            })}
        </div>
    )
}

export { RadioGroup }
