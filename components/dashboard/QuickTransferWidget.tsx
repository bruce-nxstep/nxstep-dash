"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ArrowRight, Wallet } from "lucide-react";
import { motion } from "framer-motion";

interface QuickTransferWidgetProps {
  variant?: "purple" | "gold";
}

export function QuickTransferWidget({ variant = "purple" }: QuickTransferWidgetProps) {
  const [amount, setAmount] = useState("");
  const isPurple = variant === "purple";

  const buttonGradient = isPurple
    ? "from-primary hover:from-primary-light to-primary-dark shadow-[0_0_20px_rgba(130,0,219,0.3)]"
    : "from-yellow-500 hover:from-yellow-400 to-yellow-600 shadow-[0_0_20px_rgba(234,179,8,0.3)]";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-neutral-900/90 to-black/80 backdrop-blur-3xl shadow-2xl p-6 group"
    >
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

      {/* Dynamic ambient glow */}
      <div className={`absolute -bottom-20 -right-20 h-[200px] w-[200px] rounded-full blur-[100px] opacity-20 pointer-events-none transition-opacity duration-700 group-hover:opacity-40 ${isPurple ? 'bg-primary' : 'bg-yellow-500'}`}></div>

      <div className="flex items-center justify-between mb-8 relative z-10">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/5 border border-white/10">
            <Wallet className={`h-4 w-4 ${isPurple ? 'text-primary-light' : 'text-yellow-400'}`} />
          </div>
          <h3 className="text-xs font-semibold tracking-[0.2em] text-gray-400 uppercase">Quick Transfer</h3>
        </div>
      </div>

      <div className="space-y-5 relative z-10">
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold tracking-widest text-gray-500 uppercase px-1">From Account</label>
          <div className="h-12 w-full rounded-xl border border-white/10 bg-black/40 px-4 flex items-center justify-between group-hover:bg-black/60 transition-colors">
            <span className="text-sm font-medium text-gray-200">Main Checking (*1234)</span>
            <span className="text-xs font-semibold text-gray-500">$45,200.00</span>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-bold tracking-widest text-gray-500 uppercase px-1">To Account</label>
          <div className="h-12 w-full rounded-xl border border-white/10 bg-black/40 px-4 flex items-center justify-between group-hover:bg-black/60 transition-colors">
            <span className="text-sm font-medium text-gray-200">Investment Portfolio (*9988)</span>
          </div>
        </div>

        <div className="space-y-1.5 pt-2">
          <label className="text-[10px] font-bold tracking-widest text-gray-500 uppercase px-1">Amount</label>
          <div className="relative">
            <span className="absolute left-4 top-3 text-lg font-light text-gray-400">$</span>
            <Input
              type="number"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="pl-8 bg-black/50 border-white/10 text-white placeholder:text-gray-700 text-xl font-light h-14 rounded-xl focus-visible:ring-1 focus-visible:ring-white/20 focus-visible:border-white/20 transition-all shadow-inner"
            />
          </div>
        </div>
      </div>

      <div className="mt-8 relative z-10">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`w-full flex items-center justify-center gap-2 h-12 rounded-xl text-black font-bold tracking-wide transition-all bg-gradient-to-r ${buttonGradient}`}
        >
          Execute Transfer
          <ArrowRight className="h-4 w-4" />
        </motion.button>
      </div>
    </motion.div>
  );
}
