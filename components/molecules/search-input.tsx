"use client"

import * as React from "react"
import { Search, X, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

export interface SearchInputProps
    extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
    onClear?: () => void
    loading?: boolean
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
    ({ className, value, onChange, onClear, loading, placeholder = "Search…", ...props }, ref) => {
        const hasValue = value !== undefined ? String(value).length > 0 : false

        return (
            <div className={cn("relative flex items-center w-full", className)}>
                <span className="absolute left-3 text-[var(--color-text-muted)] pointer-events-none">
                    {loading
                        ? <Loader2 className="h-4 w-4 animate-spin" />
                        : <Search className="h-4 w-4" />
                    }
                </span>
                <input
                    ref={ref}
                    type="search"
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
                    className={cn(
                        "w-full pl-9 pr-9 py-2 rounded-[var(--radius-md)] text-sm",
                        "bg-[var(--color-bg-input)] border border-[var(--color-border)]",
                        "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
                        "transition-all outline-none",
                        "hover:border-[var(--color-primary)]/40",
                        "focus:border-[var(--color-primary)]/60 focus:ring-2 focus:ring-[var(--color-primary)]/20",
                        "disabled:opacity-50 disabled:cursor-not-allowed",
                        "[&::-webkit-search-cancel-button]:hidden"
                    )}
                    {...props}
                />
                {hasValue && !loading && onClear && (
                    <button
                        type="button"
                        onClick={onClear}
                        aria-label="Clear search"
                        className="absolute right-3 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
                    >
                        <X className="h-4 w-4" />
                    </button>
                )}
            </div>
        )
    }
)
SearchInput.displayName = "SearchInput"

export { SearchInput }
