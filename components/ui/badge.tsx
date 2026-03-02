import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
    "inline-flex items-center gap-1 rounded-full font-semibold tracking-wide border transition-colors select-none",
    {
        variants: {
            variant: {
                default:
                    "bg-[var(--color-bg-card)] text-[var(--color-text-primary)] border-[var(--color-border)]",
                primary:
                    "bg-[var(--color-primary)] text-black border-transparent",
                secondary:
                    "bg-[var(--color-bg-input)] text-[var(--color-text-secondary)] border-[var(--color-border)]",
                success:
                    "bg-[var(--color-success)]/15 text-[var(--color-success)] border-[var(--color-success)]/30",
                warning:
                    "bg-[var(--color-warning)]/15 text-[var(--color-warning)] border-[var(--color-warning)]/30",
                danger:
                    "bg-[var(--color-danger)]/15 text-[var(--color-danger)] border-[var(--color-danger)]/30",
                outline:
                    "bg-transparent text-[var(--color-text-primary)] border-[var(--color-primary)]",
            },
            size: {
                sm: "px-2 py-0.5 text-[10px]",
                md: "px-2.5 py-1 text-xs",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "md",
        },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, size, ...props }: BadgeProps) {
    return (
        <span
            data-slot="badge"
            className={cn(badgeVariants({ variant, size }), className)}
            {...props}
        />
    )
}

export { Badge, badgeVariants }
