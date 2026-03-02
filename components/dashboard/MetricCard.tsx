import React from "react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { motion } from "framer-motion";

interface MetricCardProps {
    title: string;
    value: string;
    trend: number; // e.g. 12.5 for +12.5%
    variant?: "purple" | "gold";
}

export function MetricCard({ title, value, trend, variant = "purple" }: MetricCardProps) {
    const isPositive = trend >= 0;
    const isPurple = variant === "purple";

    const glowColor = isPurple ? "rgba(130, 0, 219, 0.4)" : "rgba(234, 179, 8, 0.4)";
    const bgGradient = isPurple
        ? "bg-gradient-to-br from-primary/10 to-black/40"
        : "bg-gradient-to-br from-black/90 to-neutral-900/60";

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            whileHover={{ y: -5, scale: 1.02 }}
            className={`relative group overflow-hidden rounded-3xl border border-white/10 ${bgGradient} backdrop-blur-3xl p-6 shadow-2xl`}
            style={{
                boxShadow: `0 25px 50px -12px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.1)`
            }}
        >
            {/* 
        The Magic Glass Effect: 
        1. An animated radial gradient follows the hover state (using CSS pseudo-elements or tailwind group focus).
        2. A noise overlay provides texture.
      */}
            <div
                className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
                style={{
                    background: `radial-gradient(circle at 50% 0%, ${glowColor} 0%, transparent 60%)`,
                }}
            />

            {/* The true border highlight representing light hitting the top edge */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-50"></div>

            <div className="relative z-10 flex flex-col gap-4">
                <p className="text-xs font-semibold tracking-[0.2em] text-gray-400/80 uppercase">
                    {title}
                </p>

                <div className="flex items-end justify-between">
                    <h3 className="text-4xl lg:text-5xl font-light tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-sm">
                        {value}
                    </h3>

                    <div className={`flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full border border-white/5 backdrop-blur-md ${isPositive ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'}`}>
                        {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                        {Math.abs(trend)}%
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
