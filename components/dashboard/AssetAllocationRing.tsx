"use client";

import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Sector } from "recharts";
import { motion } from "framer-motion";

// Helper: read a CSS variable value from :root at runtime
function getCSSVar(name: string, fallback: string): string {
    if (typeof window === "undefined") return fallback;
    const val = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return val || fallback;
}

const BASE_DATA = [
    { name: "Global Equities", value: 650000, cssVar: "--color-chart-equities", fallback: "#8200db" },
    { name: "Real Estate", value: 450000, cssVar: "--color-chart-real-estate", fallback: "#3b82f6" },
    { name: "Fixed Income", value: 250000, cssVar: "--color-chart-fixed-income", fallback: "#a346ff" },
    { name: "Crypto Assets", value: 100000, cssVar: "--color-chart-crypto", fallback: "#34d399" },
];

const renderActiveShape = (props: any) => {
    const RADIAN = Math.PI / 180;
    const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent } = props;
    const sin = Math.sin(-RADIAN * midAngle);
    const cos = Math.cos(-RADIAN * midAngle);

    return (
        <g>
            <text x={cx} y={cy} dy={-10} textAnchor="middle" fill={getCSSVar("--color-text-on-dark", "#fff")} className="text-2xl font-light tracking-tight">
                {payload.name}
            </text>
            <text x={cx} y={cy} dy={24} textAnchor="middle" fill={fill} className="text-xl font-bold bg-clip-text">
                {`${(percent * 100).toFixed(1)}%`}
            </text>
            {/* Outer Glowing Ring */}
            <Sector
                cx={cx}
                cy={cy}
                innerRadius={innerRadius}
                outerRadius={outerRadius + 8}
                startAngle={startAngle}
                endAngle={endAngle}
                fill={fill}
                style={{ filter: `drop-shadow(0px 0px 15px ${fill}A0)` }}
            />
            {/* Precision Inner Ring */}
            <Sector
                cx={cx}
                cy={cy}
                startAngle={startAngle}
                endAngle={endAngle}
                innerRadius={outerRadius + 12}
                outerRadius={outerRadius + 16}
                fill={fill}
            />
        </g>
    );
};

export function AssetAllocationRing() {
    const [activeIndex, setActiveIndex] = useState(0);
    const [mounted, setMounted] = useState(false);
    const [data, setData] = useState(
        BASE_DATA.map(d => ({ ...d, color: getCSSVar(d.cssVar, "transparent") }))
    );

    useEffect(() => {
        setMounted(true);
        // Read actual CSS variable values from :root now that we're in the browser
        setData(BASE_DATA.map(d => ({
            ...d,
            color: getCSSVar(d.cssVar, getCSSVar("--color-primary", "#8200db")),
        })));
    }, []);

    const onPieEnter = (_: any, index: number) => {
        setActiveIndex(index);
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="w-full relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-black/80 to-transparent backdrop-blur-3xl shadow-2xl p-6"
        >
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            <div className="mb-2">
                <h3 className="text-xs font-semibold tracking-[0.2em] text-gray-500 uppercase">Asset Allocation</h3>
            </div>

            <div className="h-[300px] flex items-center justify-center relative z-10">
                {mounted && (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            {/* @ts-ignore */}
                            <Pie
                                activeIndex={activeIndex}
                                activeShape={renderActiveShape}
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={85}
                                outerRadius={105}
                                paddingAngle={4}
                                dataKey="value"
                                onMouseEnter={onPieEnter}
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                )}
            </div>
        </motion.div>
    );
}
