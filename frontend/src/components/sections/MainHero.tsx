"use client";

import { motion } from "framer-motion";
import { ArrowRight, Check, Star, CreditCard, Clock, MessageSquare, Play } from "lucide-react";
import Link from "next/link";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function MainHero() {
    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <section id="hero" className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-[#0a0a1a] text-white pt-24 pb-12 lg:pt-32">

            {/* Background Gradient/Mesh */}
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(circle at 50% 20%, rgba(124, 58, 237, 0.15) 0%, rgba(0, 0, 0, 0) 60%)",
                }}
            />
            {/* Subtle overlay texture if wanted */}
            <div className="absolute inset-0 z-0 opacity-[0.03] bg-[url('/grid.svg')] pointer-events-none" />

            <div className="container mx-auto px-6 z-10 relative flex flex-col items-center text-center">

                {/* Badge */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="mb-6"
                >
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FF6B35]/10 border border-[#FF6B35]/30 text-[#FF6B35] text-xs uppercase font-bold tracking-widest backdrop-blur-sm">
                        <Star className="w-3 h-3 fill-current" />
                        Creazione sito gratuita
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
                    Ti creiamo il sito.{" "}
                    <span className="text-white">Gratis.</span>
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.4 }}
                    className="text-xl sm:text-2xl lg:text-3xl font-medium text-white/80 mb-6 max-w-3xl mx-auto"
                >
                    Paghi solo se ti piace. Zero rischi, zero obblighi.
                </motion.p>

                {/* Description */}
                <motion.p
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.5 }}
                    className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed"
                >
                    Raccontaci la tua attività e il nostro team crea il tuo sito professionale su misura.
                    Se non ti convince, non spendi un centesimo.
                </motion.p>

                {/* CTA Buttons */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.6 }}
                    className="flex flex-col items-center gap-4 w-full max-w-lg mx-auto mb-16"
                >
                    {/* Primary CTA */}
                    <button
                        onClick={scrollToForm}
                        className="w-full sm:w-auto px-10 py-5 bg-[#FF6B35] hover:bg-[#FF8B5E] text-white rounded-xl font-bold text-xl transition-all duration-300 transform hover:-translate-y-1 shadow-[0_10px_40px_-10px_rgba(255,107,53,0.4)] flex items-center justify-center gap-3"
                    >
                        Contattaci — è gratis
                    </button>

                    {/* Secondary CTA */}
                    <Link
                        href="/auth"
                        className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium group py-2"
                    >
                        Oppure crealo da solo in 60 secondi <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
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
                        <Star className="w-5 h-5 text-[#FF6B35] fill-[#FF6B35]" />
                        <span className="text-gray-300 text-sm font-medium">200+ attività già online</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="bg-green-500/10 p-1 rounded-full"><Check className="w-3 h-3 text-green-500" /></div>
                        <span className="text-gray-300 text-sm font-medium">Senza carta di credito</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Clock className="w-5 h-5 text-[#7C3AED]" />
                        <span className="text-gray-300 text-sm font-medium">Risposta entro 24h</span>
                    </div>
                </motion.div>

                {/* Visual Mockup/Video */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 1, ease: "easeOut" }}
                    className="mt-16 w-full max-w-5xl mx-auto"
                >
                    <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#0f0f23]/50 aspect-video group">
                        {/* Simply using the existing video for now as requested alternative */}
                        <video
                            autoPlay
                            loop
                            muted
                            playsInline
                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500"
                        >
                            <source src="/videos/hero.mp4" type="video/mp4" />
                        </video>

                        {/* Mockup Frame overlay simulation (simple border/shadow) handled by container */}
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a1a] via-transparent to-transparent opacity-60" />
                    </div>
                </motion.div>

            </div>
        </section>
    );
}
