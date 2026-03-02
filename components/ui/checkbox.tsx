"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface CheckboxProps
    extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
    label?: string
    indeterminate?: boolean
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
    ({ className, label, indeterminate, id, disabled, ...props }, ref) => {
        const internalRef = React.useRef<HTMLInputElement>(null)
        const resolvedRef = (ref as React.RefObject<HTMLInputElement>) || internalRef
        const inputId = id || React.useId()

        React.useEffect(() => {
            if (resolvedRef.current) {
                resolvedRef.current.indeterminate = !!indeterminate
            }
        }, [indeterminate, resolvedRef])

        return (
            <label
                htmlFor={inputId}
                className={cn(
                    "inline-flex items-center gap-2 cursor-pointer select-none",
                    disabled && "cursor-not-allowed opacity-50",
                    className
                )}
            >
                <span className="relative flex items-center justify-center">
                    <input
                        ref={resolvedRef}
                        id={inputId}
                        type="checkbox"
                        disabled={disabled}
                        className="peer sr-only"
                        {...props}
                    />
                    {/* Custom box */}
                    <span
                        className={cn(
                            "w-4 h-4 rounded-[var(--radius-sm)] border-2 transition-all",
                            "border-[var(--color-border)]",
                            "peer-checked:bg-[var(--color-primary)] peer-checked:border-[var(--color-primary)]",
                            "peer-indeterminate:bg-[var(--color-primary)] peer-indeterminate:border-[var(--color-primary)]",
                            "peer-focus-visible:ring-2 peer-focus-visible:ring-[var(--color-primary)]/50 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-[var(--color-bg-app)]",
                            "peer-disabled:opacity-50"
                        )}
                    >
                        {/* Check icon */}
                        <svg
                            className="absolute inset-0 m-auto w-2.5 h-2.5 text-black opacity-0 peer-checked:opacity-100 transition-opacity"
                            viewBox="0 0 10 10"
                            fill="none"
                        >
                            <path d="M1.5 5l2.5 2.5 4.5-4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        {/* Indeterminate icon */}
                        <svg
                            className="absolute inset-0 m-auto w-2.5 h-0.5 text-black opacity-0 peer-indeterminate:opacity-100 transition-opacity"
                            viewBox="0 0 10 2"
                            fill="none"
                        >
                            <path d="M1 1h8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                        </svg>
                    </span>
                </span>
                {label && (
                    <span className="text-sm text-[var(--color-text-primary)]">{label}</span>
                )}
            </label>
        )
    }
)
Checkbox.displayName = "Checkbox"

export { Checkbox }
