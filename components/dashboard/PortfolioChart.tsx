"use client";

import React, { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

const data = [
    { month: "Jan", balance: 1200000 },
    { month: "Feb", balance: 1240000 },
    { month: "Mar", balance: 1220000 },
    { month: "Apr", balance: 1350000 },
    { month: "May", balance: 1420000 },
    { month: "Jun", balance: 1400000 },
    { month: "Jul", balance: 1450000 },
];

interface PortfolioChartProps {
    variant?: "purple" | "gold";
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="rounded-xl border border-white/20 bg-black/80 px-4 py-3 shadow-[0_0_30px_rgba(0,0,0,0.8)] backdrop-blur-2xl">
                <p className="text-xs uppercase tracking-widest text-gray-500 mb-1">{label} 2026</p>
                <p className="text-2xl font-light tracking-tight text-white m-0">
                    ${payload[0].value.toLocaleString()}
                </p>
            </div>
        );
    }
    return null;
};

export function PortfolioChart({ variant = "purple" }: PortfolioChartProps) {
    const [mounted, setMounted] = useState(false);
    const isPurple = variant === "purple";

    // Read color from CSS variables at mount time
    const [strokeColor, setStrokeColor] = useState("transparent");
    useEffect(() => {
        const varName = isPurple ? "--color-chart-portfolio-purple" : "--color-chart-portfolio-gold";
        const val = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        setStrokeColor(val || (isPurple ? "#8200db" : "#eab308"));
        setMounted(true);
    }, [isPurple]);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="w-full relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-b from-black to-neutral-950 backdrop-blur-3xl shadow-2xl p-8 group"
        >
            {/* Top highlight for physical glass edge */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            {/* Ambient background glow */}
            <div className={`absolute -top-[100px] -left-[100px] w-[300px] h-[300px] rounded-full blur-[100px] opacity-10 pointer-events-none ${isPurple ? 'bg-primary' : 'bg-yellow-500'}`}></div>

            <div className="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between mb-8">
                <div>
                    <p className="text-xs font-semibold tracking-[0.2em] text-gray-500 uppercase mb-2">Portfolio Performance</p>
                    <div className="flex items-baseline gap-4">
                        <h2 className="text-5xl lg:text-6xl font-light tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-400">
                            $1,450,000<span className="text-2xl text-neutral-600">.00</span>
                        </h2>
                    </div>
                </div>
                <div className="mt-4 sm:mt-0 text-right">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold border border-white/10 backdrop-blur-md ${isPurple ? 'text-primary-light bg-primary/10' : 'text-yellow-400 bg-yellow-500/10'}`}>
                        +20.8% YTD
                    </span>
                </div>
            </div>

            <div className="h-[350px] w-full mt-[-20px] relative z-10">
                {mounted && (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data} margin={{ top: 20, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor={strokeColor} stopOpacity={0.6} />
                                    <stop offset="50%" stopColor={strokeColor} stopOpacity={0.1} />
                                    <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
                                </linearGradient>
                                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                                    <feGaussianBlur stdDeviation="8" result="blur" />
                                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                </filter>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                            <XAxis
                                dataKey="month"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 13, fontWeight: 500 }}
                                dy={15}
                            />
                            <YAxis hide domain={['dataMin - 50000', 'dataMax + 100000']} />
                            <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                            <Area
                                type="monotone"
                                dataKey="balance"
                                stroke={strokeColor}
                                strokeWidth={4}
                                fillOpacity={1}
                                fill="url(#colorBalance)"
                                activeDot={{ r: 8, fill: '#000', stroke: strokeColor, strokeWidth: 3 }}
                                style={{ filter: "url(#glow)" }}
                                animationDuration={1500}
                                animationEasing="ease-out"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>
        </motion.div>
    );
}
