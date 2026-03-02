import React from "react";
import { ArrowUpRight, ArrowDownLeft, Landmark, CreditCard, Wallet } from "lucide-react";
import { motion } from "framer-motion";

type TransactionType = "deposit" | "withdrawal" | "transfer" | "dividend" | "payment";

interface Transaction {
    id: string;
    title: string;
    date: string;
    amount: number;
    type: TransactionType;
}

const recentTransactions: Transaction[] = [
    { id: "tx1", title: "Apple Inc. Dividend", date: "Today, 10:42 AM", amount: 450.50, type: "dividend" },
    { id: "tx2", title: "Withdrawal to Chase Bank", date: "Yesterday", amount: -12000.00, type: "withdrawal" },
    { id: "tx3", title: "Monthly Deposit", date: "Oct 15, 2026", amount: 5000.00, type: "deposit" },
    { id: "tx4", title: "Amex Platinum Payment", date: "Oct 12, 2026", amount: -432.10, type: "payment" },
    { id: "tx5", title: "Internal Transfer", date: "Oct 10, 2026", amount: 15000.00, type: "transfer" },
];

const getIconForType = (type: TransactionType) => {
    switch (type) {
        case "deposit":
        case "dividend":
            return <ArrowDownLeft className="h-4 w-4 text-emerald-400" />;
        case "withdrawal":
        case "payment":
            return <ArrowUpRight className="h-4 w-4 text-rose-400" />;
        case "transfer":
            return <Landmark className="h-4 w-4" style={{ color: "var(--color-primary-light)" }} />;
        default:
            return <Wallet className="h-4 w-4 text-gray-400" />;
    }
};

const containerVariants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.1, delayChildren: 0.3 }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
};

export function TransactionList() {
    return (
        <div className="w-full relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-neutral-900/90 to-black/80 backdrop-blur-3xl shadow-2xl p-6">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

            <div className="flex flex-row items-center justify-between mb-6">
                <h3 className="text-xs font-semibold tracking-[0.2em] text-gray-500 uppercase">Recent Activity</h3>
                <button className="text-xs font-semibold tracking-wider transition-colors" style={{ color: "var(--color-primary-light)" }}>SEE ALL</button>
            </div>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="space-y-4"
            >
                {recentTransactions.map((tx) => {
                    const isPositive = tx.amount > 0;
                    const amountColor = isPositive
                        ? "text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.4)]"
                        : "text-white";

                    return (
                        <motion.div
                            key={tx.id}
                            variants={itemVariants}
                            className="flex items-center justify-between group p-2 mx(-2) rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
                        >
                            <div className="flex items-center gap-4">
                                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 shadow-inner group-hover:shadow-[0_0_15px_rgba(255,255,255,0.1)] transition-all">
                                    {getIconForType(tx.type)}
                                </div>

                                <div>
                                    <p className="text-sm font-medium tracking-tight text-gray-200 group-hover:text-white transition-colors">
                                        {tx.title}
                                    </p>
                                    <p className="text-xs text-gray-500 font-medium">
                                        {tx.date}
                                    </p>
                                </div>
                            </div>

                            <div className="text-right">
                                <p className={`text-[15px] font-semibold tracking-wide ${amountColor}`}>
                                    {isPositive ? "+" : ""}{tx.amount.toLocaleString("en-US", { style: "currency", currency: "USD" })}
                                </p>
                            </div>
                        </motion.div>
                    );
                })}
            </motion.div>
        </div>
    );
}
