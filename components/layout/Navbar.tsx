"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Menu, X } from "lucide-react";

export function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-white/70 backdrop-blur-2xl supports-[backdrop-filter]:bg-white/60 transition-all duration-300">
            <div className="container mx-auto px-6 h-24 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center space-x-2 group relative z-50">
                    <span className="text-3xl font-extrabold tracking-tighter text-slate-900 group-hover:text-primary transition-colors duration-300">
                        NXSTEP<span className="text-primary">.</span>
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:flex items-center space-x-12">
                    <Link href="/" className="text-slate-600 hover:text-primary transition-colors text-sm font-semibold tracking-wide">
                        Accueil
                    </Link>
                    <Link href="/solutions" className="text-slate-600 hover:text-primary transition-colors text-sm font-semibold tracking-wide">
                        Solutions
                    </Link>
                    <Link href="/about" className="text-slate-600 hover:text-primary transition-colors text-sm font-semibold tracking-wide">
                        À Propos
                    </Link>
                    <Link href="/contact" className="text-slate-600 hover:text-primary transition-colors text-sm font-semibold tracking-wide">
                        Contact
                    </Link>
                </div>

                {/* CTA & Mobile Menu Button */}
                <div className="flex items-center space-x-6">
                    <div className="hidden md:block">
                        <Button className="rounded-full px-8 py-6 text-sm font-bold shadow-xl shadow-primary/20 hover:shadow-primary/30 hover:-translate-y-0.5 transition-all duration-300 cursor-pointer">
                            Commencer
                        </Button>
                    </div>
                    <button
                        className="md:hidden p-2 text-slate-900 hover:bg-slate-100 rounded-full transition-colors relative z-50"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        aria-label="Toggle menu"
                    >
                        {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu Overlay */}
            {isMenuOpen && (
                <div className="fixed inset-0 bg-white z-40 flex flex-col items-center justify-center space-y-8 md:hidden animate-in fade-in slide-in-from-top-5 duration-300">
                    <Link
                        href="/"
                        className="text-2xl font-bold text-slate-900 hover:text-primary transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Accueil
                    </Link>
                    <Link
                        href="/solutions"
                        className="text-2xl font-bold text-slate-900 hover:text-primary transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Solutions
                    </Link>
                    <Link
                        href="/about"
                        className="text-2xl font-bold text-slate-900 hover:text-primary transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        À Propos
                    </Link>
                    <Link
                        href="/contact"
                        className="text-2xl font-bold text-slate-900 hover:text-primary transition-colors"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Contact
                    </Link>
                    <Button className="rounded-full px-8 py-6 text-lg font-bold shadow-xl shadow-primary/20 mt-4">
                        Commencer
                    </Button>
                </div>
            )}
        </nav>
    );
}
