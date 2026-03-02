import * as React from "react"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

export type KpiTrend = "up" | "down" | "neutral"

export interface KpiCardProps {
    label: string
    value: string | number
    unit?: string
    trend?: KpiTrend
    trendValue?: string   // e.g. "+12.4%"
    trendLabel?: string   // e.g. "vs last month"
    sparkline?: number[]  // array of values for the mini SVG chart
    icon?: React.ReactNode
    className?: string
}

function Sparkline({ data, trend }: { data: number[]; trend?: KpiTrend }) {
    if (data.length < 2) return null
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1
    const W = 80, H = 28
    const pts = data
        .map((v, i) => [
            (i / (data.length - 1)) * W,
            H - ((v - min) / range) * H,
        ])
        .map(([x, y]) => `${x},${y}`)
        .join(" ")

    const color =
        trend === "up" ? "var(--color-success)"
            : trend === "down" ? "var(--color-danger)"
                : "var(--color-text-muted)"

    return (
        <svg width={W} height={H} className="overflow-visible" aria-hidden="true">
            <polyline
                points={pts}
                fill="none"
                stroke={color}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.8"
            />
        </svg>
    )
}

function KpiCard({
    label,
    value,
    unit,
    trend,
    trendValue,
    trendLabel,
    sparkline,
    icon,
    className,
}: KpiCardProps) {
    const TrendIcon =
        trend === "up" ? TrendingUp
            : trend === "down" ? TrendingDown
                : Minus

    const trendColor =
        trend === "up" ? "text-[var(--color-success)]"
            : trend === "down" ? "text-[var(--color-danger)]"
                : "text-[var(--color-text-muted)]"

    return (
        <div
            className={cn(
                "rounded-[var(--radius-xl)] border border-[var(--color-border)]",
                "bg-[var(--color-bg-card)] p-5 flex flex-col gap-3",
                className
            )}
        >
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
                <p className="text-sm text-[var(--color-text-muted)] font-medium">{label}</p>
                {icon && (
                    <span className="text-[var(--color-text-muted)] opacity-60">{icon}</span>
                )}
            </div>

            {/* Value */}
            <div className="flex items-end gap-1">
                <span className="text-3xl font-bold text-[var(--color-text-primary)] leading-none tabular-nums">
                    {value}
                </span>
                {unit && (
                    <span className="text-sm text-[var(--color-text-muted)] mb-0.5">{unit}</span>
                )}
            </div>

            {/* Bottom: trend + sparkline */}
            <div className="flex items-center justify-between gap-2">
                {trendValue && (
                    <div className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}>
                        <TrendIcon className="h-3.5 w-3.5" />
                        <span>{trendValue}</span>
                        {trendLabel && (
                            <span className="text-[var(--color-text-muted)] font-normal">{trendLabel}</span>
                        )}
                    </div>
                )}
                {sparkline && sparkline.length > 1 && (
                    <Sparkline data={sparkline} trend={trend} />
                )}
            </div>
        </div>
    )
}

export { KpiCard }
