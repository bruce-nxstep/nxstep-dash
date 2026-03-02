"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, Variants } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link"; // Assuming you use next/link for navigation

const slides = [
    {
        id: 1,
        subtitle: "New Feature",
        title: "Your Notion-like Workspace",
        description:
            "A fast, modular, and distraction-free block editor. Manage projects, collections, and your custom Kanban boards all in one place.",
        cta: "Go to Workspace",
        link: "/workspace",
        bgGradient: "from-[#8200db]-900 to-slate-900",
    },
    {
        id: 2,
        subtitle: "Seamless Integration",
        title: "Connect 300+ Tools & Apps",
        description:
            "From Google Customer Match to Slack, we connect your favorite apps to create seamless, efficient workflows that just work.",
        cta: "See Integrations",
        link: "/integrations",
        bgGradient: "from-indigo-900 to-purple-900",
    },
    {
        id: 3,
        subtitle: "Transform Your Business",
        title: "Ready to Automate?",
        description:
            "Join the businesses that have revolutionized their operations with Nxstep. Custom workflows, dedicated support, and 40% efficiency gains await.",
        cta: "Get Started",
        link: "/contact", // Example link
        bgGradient: "from-slate-900 to-emerald-900",
    },
];

const variants = {
    enter: (direction: number) => ({
        x: direction > 0 ? 1000 : -1000,
        opacity: 0,
    }),
    center: {
        zIndex: 1,
        x: 0,
        opacity: 1,
    },
    exit: (direction: number) => ({
        zIndex: 0,
        x: direction < 0 ? 1000 : -1000,
        opacity: 0,
    }),
};

const textVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: (custom: number) => ({
        opacity: 1,
        y: 0,
        transition: { delay: custom * 0.1, duration: 0.5, ease: "easeOut" },
    }),
};

export function PresentationHero() {
    const [[page, direction], setPage] = useState([0, 0]);
    const [isAutoPlaying, setIsAutoPlaying] = useState(true);

    // We only have 3 slides, so we wrap around using modulo
    const imageIndex = Math.abs(page % slides.length);
    const currentSlide = slides[imageIndex];

    const paginate = (newDirection: number) => {
        setPage([page + newDirection, newDirection]);
    };

    useEffect(() => {
        if (!isAutoPlaying) return;

        const timer = setInterval(() => {
            paginate(1);
        }, 6000); // 6 seconds per slide

        return () => clearInterval(timer);
    }, [page, isAutoPlaying]);

    return (
        <section
            className="relative h-[85vh] min-h-[600px] w-full overflow-hidden bg-slate-950 text-white"
            onMouseEnter={() => setIsAutoPlaying(false)}
            onMouseLeave={() => setIsAutoPlaying(true)}
        >
            {/* Background Gradient with Transition */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentSlide.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 1 }}
                    className={`absolute inset-0 bg-gradient-to-br ${currentSlide.bgGradient} opacity-50`}
                />
            </AnimatePresence>

            {/* Abstract Background Element */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-3xl -z-10 animate-pulse" />


            <div className="container relative z-10 mx-auto px-4 h-full flex flex-col justify-center">
                <AnimatePresence initial={false} custom={direction} mode="wait">
                    <motion.div
                        key={page}
                        custom={direction}
                        variants={variants}
                        initial="enter"
                        animate="center"
                        exit="exit"
                        transition={{
                            x: { type: "spring", stiffness: 300, damping: 30 },
                            opacity: { duration: 0.2 },
                        }}
                        className="w-full max-w-4xl mx-auto text-center"
                    >
                        <motion.span
                            custom={1}
                            variants={textVariants}
                            initial="hidden"
                            animate="visible"
                            className="inline-block py-1 px-3 rounded-full bg-white/10 border border-white/20 text-sm font-medium tracking-wider mb-6 text-primary-foreground"
                        >
                            {currentSlide.subtitle}
                        </motion.span>

                        <motion.h1
                            custom={2}
                            variants={textVariants}
                            initial="hidden"
                            animate="visible"
                            className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 leading-tight"
                        >
                            {currentSlide.title}
                        </motion.h1>

                        <motion.p
                            custom={3}
                            variants={textVariants}
                            initial="hidden"
                            animate="visible"
                            className="text-lg md:text-xl text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed"
                        >
                            {currentSlide.description}
                        </motion.p>

                        <motion.div
                            custom={4}
                            variants={textVariants}
                            initial="hidden"
                            animate="visible"
                            className="flex flex-col sm:flex-row items-center justify-center gap-4"
                        >
                            <Button size="lg" className="w-full sm:w-auto gap-2 text-md h-12 px-8" asChild>
                                <Link href={currentSlide.link}>
                                    {currentSlide.cta} <ArrowRight className="h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                variant="outline"
                                size="lg"
                                className="w-full sm:w-auto text-md h-12 px-8 border-white/20 hover:bg-white/10 text-slate-900" // Added text-slate-900 for visibility on light bg if any locally, but mostly for contrast
                            >
                                Learn More
                            </Button>
                        </motion.div>
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Navigation Arrows */}
            <div className="absolute inset-y-0 left-4 z-20 flex items-center">
                <button
                    onClick={() => paginate(-1)}
                    className="p-3 rounded-full bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm transition-all"
                >
                    <ChevronLeft className="h-6 w-6" />
                </button>
            </div>
            <div className="absolute inset-y-0 right-4 z-20 flex items-center">
                <button
                    onClick={() => paginate(1)}
                    className="p-3 rounded-full bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm transition-all"
                >
                    <ChevronRight className="h-6 w-6" />
                </button>
            </div>

            {/* Dots */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex gap-3">
                {slides.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => setPage([index, index > imageIndex ? 1 : -1])}
                        className={`w-3 h-3 rounded-full transition-all duration-300 ${index === imageIndex ? "bg-primary w-8" : "bg-white/30 hover:bg-white/50"
                            }`}
                    />
                ))}
            </div>
        </section>
    );
}
