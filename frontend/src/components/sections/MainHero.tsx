"use client";

import { motion } from "framer-motion";
import { ArrowRight, Check, Star, Clock } from "lucide-react";
import Link from "next/link";
import { useLanguage, translations } from "@/lib/i18n";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function MainHero() {
    const { language } = useLanguage();
    const txt = translations[language].heroAgency;

    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

    const videoSrc = language === "en" ? "/videos/hero-en.mp4" : "/videos/hero-tutorial.mp4";

    return (
        <section id="hero" className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-[#0a0a1a] text-white pt-24 pb-12 lg:pt-32">

            {/* Background Gradient - BLUE */}
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(circle at 50% 20%, rgba(0, 144, 255, 0.15) 0%, rgba(0, 0, 0, 0) 60%)",
                }}
            />
            <div className="absolute inset-0 z-0 opacity-[0.03] bg-[url('/grid.svg')] pointer-events-none" />

            <div className="container mx-auto px-6 z-10 relative flex flex-col items-center text-center">

                {/* Badge */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="mb-6"
                >
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0090FF]/10 border border-[#0090FF]/30 text-[#0090FF] text-xs uppercase font-bold tracking-widest backdrop-blur-sm">
                        <Star className="w-3 h-3 fill-current" />
                        {txt.badge}
                    </span>
                </motion.div>

                {/* Main Title */}
                <motion.h1
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.2 }}
                    className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6 max-w-5xl mx-auto"
                >
                    {txt.title}{" "}
                    <span className="text-white">{txt.titleHighlight}</span>
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.4 }}
                    className="text-xl sm:text-2xl lg:text-3xl font-medium text-white/80 mb-6 max-w-3xl mx-auto"
                >
                    {txt.subtitle}
                </motion.p>

                {/* Description */}
                <motion.p
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.5 }}
                    className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed"
                >
                    {txt.description}
                    {" "}{txt.descriptionLine2}
                </motion.p>

                {/* CTA Buttons */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.6 }}
                    className="flex flex-col items-center gap-4 w-full max-w-lg mx-auto mb-16"
                >
                    {/* Primary CTA - BLUE */}
                    <button
                        onClick={scrollToForm}
                        className="w-full sm:w-auto px-10 py-5 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-xl transition-all duration-300 transform hover:-translate-y-1 shadow-[0_10px_40px_-10px_rgba(0,144,255,0.4)] flex items-center justify-center gap-3"
                    >
                        {txt.cta}
                    </button>

                    {/* Secondary CTA */}
                    <Link
                        href="/auth"
                        className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium group py-2"
                    >
                        {txt.ctaSecondary} <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </motion.div>

                {/* Trust Badges */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.8 }}
                    className="flex flex-wrap justify-center items-center gap-6 sm:gap-10 border-t border-white/5 pt-8 w-full max-w-4xl"
                >
                    <div className="flex items-center gap-2">
                        <Star className="w-5 h-5 text-[#0090FF] fill-[#0090FF]" />
                        <span className="text-gray-300 text-sm font-medium">{txt.trustBadges[0]}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="bg-green-500/10 p-1 rounded-full"><Check className="w-3 h-3 text-green-500" /></div>
                        <span className="text-gray-300 text-sm font-medium">{txt.trustBadges[1]}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-[#0090FF]" />
                        <span className="text-gray-300 text-sm font-medium">{txt.trustBadges[2]}</span>
                    </div>
                </motion.div>

                {/* Video */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 1, ease: "easeOut" }}
                    className="mt-16 w-full max-w-5xl mx-auto"
                >
                    <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#0f0f23]/50 aspect-video group">
                        <video
                            key={videoSrc}
                            src={videoSrc}
                            autoPlay
                            muted
                            loop
                            playsInline
                            className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a1a] via-transparent to-transparent opacity-20 pointer-events-none" />
                    </div>
                </motion.div>

            </div>
        </section>
    );
}
