"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ── Types ────────────────────────────────────────────────────────────────────
interface ContentItem {
    id: number;
    title: string;
    post_idea: string;
    post_type: string;
    content: string;
    status: string;
    scheduled_at: string | null;
    created_at: string;
    updated_at: string;
}

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

// ── Status Config ────────────────────────────────────────────────────────────
const STATUS_CONFIG: Record<string, { color: string; bg: string; border: string; label: string }> = {
    Brouillon: { color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/20", label: "Brouillon" },
    "Prêt": { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", label: "Prêt" },
    Published: { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "Publié" },
};

const CAL_COLORS: Record<string, string> = {
    Brouillon: "bg-slate-600",
    "Prêt": "bg-amber-500",
    Published: "bg-emerald-500",
};

// ── Calendar Helpers ─────────────────────────────────────────────────────────
const WEEKDAYS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
const MONTHS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

function getCalendarDays(year: number, month: number) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    // Monday-start: getDay() returns 0=Sun, we want 0=Mon
    let startOffset = firstDay.getDay() - 1;
    if (startOffset < 0) startOffset = 6;

    const days: (number | null)[] = [];
    for (let i = 0; i < startOffset; i++) days.push(null);
    for (let d = 1; d <= lastDay.getDate(); d++) days.push(d);
    return days;
}

function formatDate(d: string | null) {
    if (!d) return "—";
    try {
        const dt = new Date(d);
        return dt.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
    } catch {
        return d;
    }
}

// ── Quick Actions ────────────────────────────────────────────────────────────
const QUICK_ACTIONS = [
    { icon: "📅", label: "Plan de la semaine", prompt: "Montre-moi le planning éditorial de cette semaine et propose des idées de posts LinkedIn pour les jours vides." },
    { icon: "🎠", label: "Créer un carrousel", prompt: "Aide-moi à créer un carrousel LinkedIn de 5 slides sur un sujet tendance IA. Propose la structure et le contenu de chaque slide." },
    { icon: "✍️", label: "Rédiger un post", prompt: "Rédige un post LinkedIn engageant pour NXSTEP sur le thème de l'automatisation IA en B2B. Style professionnel mais humain." },
    { icon: "📊", label: "Stratégie", prompt: "Propose-moi une stratégie de contenu LinkedIn pour le mois prochain : thèmes, fréquence, types de posts." },
];

// ══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════════════════════════════════════
export default function CommunityPage() {
    // ── State ────────────────────────────────────────────────────────────────
    const [items, setItems] = useState<ContentItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [messages, setMessages] = useState<ChatMessage[]>([
        { role: "assistant", content: "Salut ! Je suis **Joy**, votre Community Manager 📱✨\n\nJe vous aide à planifier vos posts LinkedIn et vos carrousels. Prêt à faire exploser votre visibilité ?" },
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [calMonth, setCalMonth] = useState(new Date().getMonth());
    const [calYear, setCalYear] = useState(new Date().getFullYear());
    const [editingItem, setEditingItem] = useState<ContentItem | null>(null);

    const chatEndRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);

    // ── Fetch Content Plan ───────────────────────────────────────────────────
    const fetchItems = useCallback(async () => {
        try {
            const res = await fetch("/api/content-plan");
            const data = await res.json();
            setItems(data.items || []);
        } catch (err) {
            console.error("Fetch error:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchItems(); }, [fetchItems]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isTyping]);

    // ── Chat Handler ─────────────────────────────────────────────────────────
    const sendMessage = async (text?: string) => {
        const msg = text || input.trim();
        if (!msg) return;

        const userMsg: ChatMessage = { role: "user", content: msg };
        const newHistory = [...messages, userMsg];
        setMessages(newHistory);
        setInput("");
        setIsTyping(true);

        try {
            const res = await fetch("/api/community-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: msg,
                    history: messages.filter((_, i) => i > 0), // skip welcome
                }),
            });
            const data = await res.json();
            setMessages([...newHistory, { role: "assistant", content: data.response || "Erreur." }]);
        } catch {
            setMessages([...newHistory, { role: "assistant", content: "Désolé, une erreur est survenue." }]);
        } finally {
            setIsTyping(false);
        }
    };

    // ── CRUD Handlers ────────────────────────────────────────────────────────
    const createItem = async (title: string, scheduled_at?: string) => {
        try {
            await fetch("/api/content-plan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, scheduled_at, status: "Brouillon", post_type: "Post" }),
            });
            fetchItems();
        } catch (err) {
            console.error("Create error:", err);
        }
    };

    const updateItem = async (id: number, updates: Partial<ContentItem>) => {
        try {
            await fetch(`/api/content-plan/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updates),
            });
            fetchItems();
            setEditingItem(null);
        } catch (err) {
            console.error("Update error:", err);
        }
    };

    const deleteItem = async (id: number) => {
        try {
            await fetch(`/api/content-plan?id=${id}`, { method: "DELETE" });
            fetchItems();
        } catch (err) {
            console.error("Delete error:", err);
        }
    };

    // ── Computed ─────────────────────────────────────────────────────────────
    const stats = {
        total: items.length,
        brouillon: items.filter((i) => i.status === "Brouillon").length,
        pret: items.filter((i) => i.status === "Prêt").length,
        published: items.filter((i) => i.status === "Published").length,
    };

    const calDays = getCalendarDays(calYear, calMonth);
    const today = new Date();

    function getEventsForDay(day: number) {
        const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        return items.filter((it) => it.scheduled_at?.startsWith(dateStr));
    }

    // ══════════════════════════════════════════════════════════════════════════
    // RENDER
    // ══════════════════════════════════════════════════════════════════════════
    return (
        <div className="min-h-screen bg-[#191022] text-slate-100 font-sans">
            <div className="max-w-[1600px] mx-auto px-6 py-8">

                {/* ── Header ────────────────────────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="flex items-center gap-4 mb-2">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-2xl shadow-lg shadow-purple-500/20">
                            📱
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                                Community Manager
                            </h1>
                            <p className="text-sm text-slate-400">
                                Pilotez votre calendrier éditorial LinkedIn avec Joy
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* ── KPI Metrics ───────────────────────────────────────────── */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {[
                        { label: "Total Posts", value: stats.total, icon: "📝", gradient: "from-purple-500/20 to-transparent" },
                        { label: "Brouillons", value: stats.brouillon, icon: "📋", gradient: "from-slate-500/20 to-transparent" },
                        { label: "Prêts", value: stats.pret, icon: "⚡", gradient: "from-amber-500/20 to-transparent" },
                        { label: "Publiés", value: stats.published, icon: "🚀", gradient: "from-emerald-500/20 to-transparent" },
                    ].map((kpi, i) => (
                        <motion.div
                            key={kpi.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.08 }}
                            className={`relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br ${kpi.gradient} backdrop-blur-xl p-5`}
                        >
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-xs font-semibold tracking-widest text-slate-400 uppercase">{kpi.label}</span>
                                <span className="text-xl">{kpi.icon}</span>
                            </div>
                            <span className="text-3xl font-bold tracking-tight">{kpi.value}</span>
                        </motion.div>
                    ))}
                </div>

                {/* ── Quick Actions ─────────────────────────────────────────── */}
                <div className="flex gap-3 mb-8 flex-wrap">
                    {QUICK_ACTIONS.map((qa) => (
                        <button
                            key={qa.label}
                            onClick={() => sendMessage(qa.prompt)}
                            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm text-slate-300 hover:bg-purple-500/10 hover:border-purple-500/30 hover:text-white transition-all duration-200"
                        >
                            <span>{qa.icon}</span>
                            <span>{qa.label}</span>
                        </button>
                    ))}
                </div>

                {/* ── Main Grid: Calendar + Chat ─────────────────────────── */}
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">

                    {/* ── Calendar (3 cols) ──────────────────────────────────── */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-3 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
                    >
                        {/* Calendar Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                            <h2 className="text-lg font-bold tracking-tight">📅 Calendrier Éditorial</h2>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => { if (calMonth === 0) { setCalMonth(11); setCalYear(calYear - 1); } else setCalMonth(calMonth - 1); }}
                                    className="p-2 rounded-lg hover:bg-white/10 transition-colors text-slate-400 hover:text-white"
                                >
                                    ←
                                </button>
                                <span className="text-sm font-semibold min-w-[140px] text-center">
                                    {MONTHS_FR[calMonth]} {calYear}
                                </span>
                                <button
                                    onClick={() => { if (calMonth === 11) { setCalMonth(0); setCalYear(calYear + 1); } else setCalMonth(calMonth + 1); }}
                                    className="p-2 rounded-lg hover:bg-white/10 transition-colors text-slate-400 hover:text-white"
                                >
                                    →
                                </button>
                            </div>
                        </div>

                        {/* Weekday Headers */}
                        <div className="grid grid-cols-7 border-b border-white/5">
                            {WEEKDAYS.map((wd) => (
                                <div key={wd} className="text-center text-[11px] font-semibold text-slate-500 uppercase tracking-wider py-2">
                                    {wd}
                                </div>
                            ))}
                        </div>

                        {/* Day Grid */}
                        <div className="grid grid-cols-7">
                            {calDays.map((day, idx) => {
                                const isToday = day !== null && calYear === today.getFullYear() && calMonth === today.getMonth() && day === today.getDate();
                                const events = day ? getEventsForDay(day) : [];

                                return (
                                    <div
                                        key={idx}
                                        className={`min-h-[90px] border-b border-r border-white/5 p-1.5 relative group
                      ${day ? "hover:bg-white/[0.03] cursor-pointer" : "bg-white/[0.01]"}
                      ${isToday ? "bg-purple-500/[0.06]" : ""}
                    `}
                                        onClick={() => {
                                            if (day) {
                                                const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                                                const title = prompt("Titre du nouveau post :");
                                                if (title) createItem(title, dateStr);
                                            }
                                        }}
                                    >
                                        {day && (
                                            <>
                                                <span className={`text-xs font-medium ${isToday ? "bg-purple-500 text-white rounded-full w-6 h-6 flex items-center justify-center" : "text-slate-500"}`}>
                                                    {day}
                                                </span>
                                                <div className="mt-1 space-y-0.5">
                                                    {events.slice(0, 3).map((evt) => (
                                                        <div
                                                            key={evt.id}
                                                            onClick={(e) => { e.stopPropagation(); setEditingItem(evt); }}
                                                            className={`${CAL_COLORS[evt.status] || "bg-slate-600"} text-white text-[10px] font-medium px-1.5 py-0.5 rounded truncate cursor-pointer hover:opacity-80 transition-opacity`}
                                                            title={evt.title}
                                                        >
                                                            {evt.post_type === "Carousel" ? "🎠" : "📝"} {evt.title}
                                                        </div>
                                                    ))}
                                                    {events.length > 3 && (
                                                        <span className="text-[10px] text-slate-500">+{events.length - 3} more</span>
                                                    )}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Legend */}
                        <div className="flex gap-6 px-6 py-3 border-t border-white/5">
                            {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
                                <div key={key} className="flex items-center gap-2">
                                    <div className={`w-2.5 h-2.5 rounded-full ${CAL_COLORS[key]}`} />
                                    <span className="text-[11px] text-slate-400">{cfg.label}</span>
                                </div>
                            ))}
                        </div>
                    </motion.div>

                    {/* ── Chat with Joy (2 cols) ─────────────────────────────── */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-2 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl flex flex-col overflow-hidden"
                        style={{ height: "calc(90px * 6 + 120px)" }} // match calendar height
                    >
                        {/* Chat Header */}
                        <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center text-lg shadow-md">
                                🤖
                            </div>
                            <div>
                                <h3 className="text-sm font-bold">Joy — Community Manager</h3>
                                <p className="text-[11px] text-slate-400">Stratégie LinkedIn & contenu</p>
                            </div>
                            <div className="ml-auto flex items-center gap-1.5">
                                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">En ligne</span>
                            </div>
                        </div>

                        {/* Messages */}
                        <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
                            <AnimatePresence>
                                {messages.map((msg, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                    >
                                        <div
                                            className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${msg.role === "user"
                                                    ? "bg-purple-600 text-white rounded-br-sm"
                                                    : "bg-white/[0.06] border border-white/10 text-slate-200 rounded-bl-sm"
                                                }`}
                                        >
                                            {msg.content}
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="bg-white/[0.06] border border-white/10 rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1.5 items-center">
                                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                        <div className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" />
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Input */}
                        <div className="p-3 border-t border-white/10">
                            <form
                                onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
                                className="relative flex items-center"
                            >
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Demandez à Joy de créer un post…"
                                    disabled={isTyping}
                                    className="w-full bg-white/[0.05] border border-white/10 rounded-xl pl-4 pr-12 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/40 focus:border-purple-500/40 transition-all disabled:opacity-50"
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isTyping}
                                    className="absolute right-2 p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                >
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                    </svg>
                                </button>
                            </form>
                        </div>
                    </motion.div>
                </div>

                {/* ── Content Plan Table ──────────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
                >
                    <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                        <h2 className="text-lg font-bold tracking-tight">📋 Planning Éditorial</h2>
                        <button
                            onClick={() => {
                                const title = prompt("Titre du nouveau post :");
                                if (title) createItem(title);
                            }}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 text-white text-sm font-medium hover:bg-purple-500 transition-colors shadow-lg shadow-purple-500/20"
                        >
                            + Nouveau post
                        </button>
                    </div>

                    {loading ? (
                        <div className="p-12 text-center text-slate-500">Chargement…</div>
                    ) : items.length === 0 ? (
                        <div className="p-12 text-center">
                            <p className="text-slate-400 mb-4">Le planning éditorial est vide.</p>
                            <p className="text-sm text-slate-500">Demandez à Joy de créer vos premiers posts ! 🚀</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider border-b border-white/5">
                                        <th className="px-6 py-3">Titre</th>
                                        <th className="px-4 py-3">Type</th>
                                        <th className="px-4 py-3">Statut</th>
                                        <th className="px-4 py-3">Prévu le</th>
                                        <th className="px-4 py-3">💡 Idée</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items.map((item) => {
                                        const sc = STATUS_CONFIG[item.status] || STATUS_CONFIG.Brouillon;
                                        return (
                                            <tr
                                                key={item.id}
                                                className="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
                                            >
                                                <td className="px-6 py-3.5 font-medium text-white max-w-[240px] truncate">
                                                    {item.title}
                                                </td>
                                                <td className="px-4 py-3.5">
                                                    <span className="inline-flex items-center gap-1 text-xs text-slate-300">
                                                        {item.post_type === "Carousel" ? "🎠" : "📝"} {item.post_type}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3.5">
                                                    <span className={`inline-flex px-2.5 py-1 rounded-full text-[11px] font-semibold ${sc.color} ${sc.bg} border ${sc.border}`}>
                                                        {sc.label}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3.5 text-slate-400 text-xs">
                                                    {formatDate(item.scheduled_at)}
                                                </td>
                                                <td className="px-4 py-3.5 text-slate-400 text-xs max-w-[200px] truncate">
                                                    {item.post_idea || "—"}
                                                </td>
                                                <td className="px-4 py-3.5 text-right">
                                                    <div className="flex items-center justify-end gap-1">
                                                        <button
                                                            onClick={() => setEditingItem(item)}
                                                            className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                                                            title="Modifier"
                                                        >
                                                            ✏️
                                                        </button>
                                                        <select
                                                            value={item.status}
                                                            onChange={(e) => updateItem(item.id, { status: e.target.value })}
                                                            className="bg-transparent border border-white/10 rounded-lg px-2 py-1 text-[11px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-purple-500/40 cursor-pointer"
                                                        >
                                                            <option value="Brouillon" className="bg-[#191022]">Brouillon</option>
                                                            <option value="Prêt" className="bg-[#191022]">Prêt</option>
                                                            <option value="Published" className="bg-[#191022]">Publié</option>
                                                        </select>
                                                        <button
                                                            onClick={() => { if (confirm(`Supprimer "${item.title}" ?`)) deleteItem(item.id); }}
                                                            className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors"
                                                            title="Supprimer"
                                                        >
                                                            🗑️
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </motion.div>

                {/* ── Edit Modal ──────────────────────────────────────────── */}
                <AnimatePresence>
                    {editingItem && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
                            onClick={() => setEditingItem(null)}
                        >
                            <motion.div
                                initial={{ scale: 0.95, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.95, opacity: 0 }}
                                onClick={(e) => e.stopPropagation()}
                                className="bg-[#1f142b] border border-white/10 rounded-2xl p-6 w-full max-w-lg shadow-2xl"
                            >
                                <h3 className="text-lg font-bold mb-4">✏️ Modifier la publication</h3>
                                <div className="space-y-4">
                                    <div>
                                        <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">Titre</label>
                                        <input
                                            type="text"
                                            defaultValue={editingItem.title}
                                            id="edit-title"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">Type</label>
                                            <select
                                                defaultValue={editingItem.post_type}
                                                id="edit-type"
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                            >
                                                <option value="Post" className="bg-[#1f142b]">Post</option>
                                                <option value="Carousel" className="bg-[#1f142b]">Carousel</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">Statut</label>
                                            <select
                                                defaultValue={editingItem.status}
                                                id="edit-status"
                                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                            >
                                                <option value="Brouillon" className="bg-[#1f142b]">Brouillon</option>
                                                <option value="Prêt" className="bg-[#1f142b]">Prêt</option>
                                                <option value="Published" className="bg-[#1f142b]">Publié</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div>
                                        <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">Date prévue</label>
                                        <input
                                            type="date"
                                            defaultValue={editingItem.scheduled_at?.split("T")[0] || ""}
                                            id="edit-date"
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">💡 Idée / Notes</label>
                                        <textarea
                                            defaultValue={editingItem.post_idea || ""}
                                            id="edit-idea"
                                            rows={3}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40 resize-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1 block">Contenu du post</label>
                                        <textarea
                                            defaultValue={editingItem.content || ""}
                                            id="edit-content"
                                            rows={4}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500/40 resize-none"
                                        />
                                    </div>
                                </div>
                                <div className="flex gap-3 mt-6">
                                    <button
                                        onClick={() => {
                                            updateItem(editingItem.id, {
                                                title: (document.getElementById("edit-title") as HTMLInputElement).value,
                                                post_type: (document.getElementById("edit-type") as HTMLSelectElement).value,
                                                status: (document.getElementById("edit-status") as HTMLSelectElement).value,
                                                scheduled_at: (document.getElementById("edit-date") as HTMLInputElement).value || null,
                                                post_idea: (document.getElementById("edit-idea") as HTMLTextAreaElement).value,
                                                content: (document.getElementById("edit-content") as HTMLTextAreaElement).value,
                                            });
                                        }}
                                        className="flex-1 py-2.5 rounded-xl bg-purple-600 text-white font-medium text-sm hover:bg-purple-500 transition-colors shadow-lg shadow-purple-500/20"
                                    >
                                        Sauvegarder
                                    </button>
                                    <button
                                        onClick={() => setEditingItem(null)}
                                        className="px-6 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm text-slate-300 hover:bg-white/10 transition-colors"
                                    >
                                        Annuler
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>
        </div>
    );
}
