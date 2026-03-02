import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const avatarVariants = cva(
    "relative inline-flex items-center justify-center rounded-full font-semibold shrink-0 overflow-hidden select-none",
    {
        variants: {
            size: {
                xs: "w-6 h-6 text-[10px]",
                sm: "w-8 h-8 text-xs",
                md: "w-10 h-10 text-sm",
                lg: "w-14 h-14 text-base",
                xl: "w-20 h-20 text-xl",
            },
        },
        defaultVariants: { size: "md" },
    }
)

export interface AvatarProps
    extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof avatarVariants> {
    src?: string
    alt?: string
    initials?: string
}

function Avatar({ className, size, src, alt, initials, ...props }: AvatarProps) {
    const [imgError, setImgError] = React.useState(false)
    const showFallback = !src || imgError

    return (
        <span
            data-slot="avatar"
            className={cn(
                avatarVariants({ size }),
                showFallback
                    ? "bg-[var(--color-primary)]/20 text-[var(--color-primary)] border border-[var(--color-primary)]/30"
                    : "bg-[var(--color-bg-card)]",
                className
            )}
            {...props}
        >
            {!showFallback && (
                <img
                    src={src}
                    alt={alt ?? "Avatar"}
                    className="w-full h-full object-cover"
                    onError={() => setImgError(true)}
                />
            )}
            {showFallback && (
                <span aria-hidden="true">
                    {initials ?? "?"}
                </span>
            )}
        </span>
    )
}

export { Avatar, avatarVariants }
