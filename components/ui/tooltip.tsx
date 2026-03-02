"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface TooltipProps {
    content: React.ReactNode
    children: React.ReactElement
    side?: "top" | "bottom" | "left" | "right"
    delay?: number
    className?: string
}

function Tooltip({ content, children, side = "top", delay = 400, className }: TooltipProps) {
    const [visible, setVisible] = React.useState(false)
    const timerRef = React.useRef<ReturnType<typeof setTimeout>>()

    const show = () => {
        timerRef.current = setTimeout(() => setVisible(true), delay)
    }
    const hide = () => {
        clearTimeout(timerRef.current)
        setVisible(false)
    }

    const posClasses = {
        top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
        bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
        left: "right-full top-1/2 -translate-y-1/2 mr-2",
        right: "left-full top-1/2 -translate-y-1/2 ml-2",
    }[side]

    return (
        <span
            className="relative inline-flex"
            onMouseEnter={show}
            onMouseLeave={hide}
            onFocus={show}
            onBlur={hide}
        >
            {children}
            {visible && (
                <span
                    role="tooltip"
                    className={cn(
                        "absolute z-50 pointer-events-none whitespace-nowrap",
                        "px-2.5 py-1.5 rounded-[var(--radius-md)]",
                        "bg-[var(--color-bg-card)] border border-[var(--color-border)]",
                        "text-xs text-[var(--color-text-primary)] shadow-lg",
                        "animate-in fade-in-0 zoom-in-95 duration-100",
                        posClasses,
                        className
                    )}
                >
                    {content}
                </span>
            )}
        </span>
    )
}

export { Tooltip }
