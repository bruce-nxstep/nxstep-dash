import * as React from "react"
import { cn } from "@/lib/utils"

export interface FormFieldProps {
    label?: string
    htmlFor?: string
    helper?: string
    error?: string
    required?: boolean
    className?: string
    children: React.ReactNode
}

function FormField({
    label,
    htmlFor,
    helper,
    error,
    required,
    className,
    children,
}: FormFieldProps) {
    return (
        <div className={cn("flex flex-col gap-1.5 w-full", className)}>
            {label && (
                <label
                    htmlFor={htmlFor}
                    className="text-sm font-medium text-[var(--color-text-primary)]"
                >
                    {label}
                    {required && (
                        <span
                            aria-hidden="true"
                            className="ml-1 text-[var(--color-danger)]"
                        >
                            *
                        </span>
                    )}
                </label>
            )}
            {children}
            {error ? (
                <p role="alert" className="text-xs text-[var(--color-danger)] flex items-center gap-1">
                    <svg className="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {error}
                </p>
            ) : helper ? (
                <p className="text-xs text-[var(--color-text-muted)]">{helper}</p>
            ) : null}
        </div>
    )
}

export { FormField }
