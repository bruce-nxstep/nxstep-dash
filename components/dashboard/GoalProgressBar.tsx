"use client";

import React from "react";
import { Target, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

interface GoalProgressBarProps {
    variant?: "purple" | "gold";
}

export function GoalProgressBar({ variant = "purple" }: GoalProgressBarProps) {
    const goalAmount = 2000000;
    const currentAmount = 1450000;
    const progressPercent = (currentAmount / goalAmount) * 100;
    const isPurple = variant === "purple";
    const accentColor = isPurple ? "rgba(130, 0, 219, 0.4)" : "rgba(234, 179, 8, 0.4)";
    const fillGradient = isPurple
        ? "from-primary via-primary-light to-primary-light"
        : "from-yellow-600 via-yellow-400 to-yellow-300";

    return (
        <div className="w-full relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-black/80 to-neutral-900/60 backdrop-blur-3xl shadow-2xl p-6 group">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            {/* Background ambient glow effect */}
            <div className={`absolute -bottom-20 -right-20 h-[200px] w-[200px] rounded-full blur-[100px] transition-opacity duration-700 opacity-0 group-hover:opacity-100 pointer-events-none ${isPurple ? 'bg-primary/20' : 'bg-yellow-500/20'}`}></div>

            <div className="flex items-center justify-between mb-8 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/5 border border-white/10">
                        <Target className={`h-4 w-4 ${isPurple ? 'text-primary-light' : 'text-yellow-400'}`} />
                    </div>
                    <h3 className="text-xs font-semibold tracking-[0.2em] text-gray-400 uppercase">Retirement Goal</h3>
                </div>
                <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-white/5 backdrop-blur-md">
                    <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
                    <span className="text-xs font-bold text-emerald-400 tracking-wide cursor-default">ON TRACK</span>
                </div>
            </div>

            <div className="space-y-6 relative z-10">
                <div className="flex items-end justify-between">
                    <div>
                        <p className="text-[10px] font-bold tracking-widest text-gray-500 uppercase mb-1">Current</p>
                        <p className="text-3xl font-light text-white tracking-tight">
                            ${(currentAmount / 1000000).toFixed(2)}M
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] font-bold tracking-widest text-gray-500 uppercase mb-1">Target</p>
                        <p className="text-xl font-light text-gray-400 tracking-tight">
                            ${(goalAmount / 1000000).toFixed(2)}M
                        </p>
                    </div>
                </div>

                <div className="relative pt-2">
                    {/* Track Background */}
                    <div className="h-3 w-full rounded-full bg-white/5 border border-white/5 shadow-inner overflow-hidden relative">

                        {/* Animated Fill */}
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progressPercent}%` }}
                            transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
                            className={`absolute top-0 left-0 h-full rounded-full bg-gradient-to-r ${fillGradient} shadow-[0_0_15px_rgba(130,0,219,0.6)]`}
                        />
                    </div>

                    <div className="mt-4 flex justify-between items-center text-xs text-gray-500 font-medium">
                        <span>0%</span>
                        <span className={`${isPurple ? 'text-primary-light' : 'text-yellow-400'} font-bold`}>{progressPercent.toFixed(1)}% Completed</span>
                        <span>100%</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
