"use client";

import { motion } from "framer-motion";
import { ArrowRight, Check, ChevronDown, MessageSquare } from "lucide-react";
import Link from "next/link";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function MainHero() {
    const scrollToNextSection = () => {
        const nextSection = document.getElementById("ai-app-hero");
        if (nextSection) {
            nextSection.scrollIntoView({ behavior: "smooth" });
        }
    };

    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-black text-white pt-20 pb-10">
            {/* Dynamic Background */}
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(circle at 50% 30%, rgba(29, 78, 216, 0.15) 0%, rgba(0, 0, 0, 0) 70%)",
                }}
            />

            {/* Subtle Glow behind title */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none z-0" />

            <div className="container mx-auto px-4 z-10 relative flex flex-col items-center text-center">

                {/* Badge */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="mb-8"
                >
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-900/20 border border-blue-500/20 text-blue-400 text-sm font-semibold tracking-wide backdrop-blur-sm">
                        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        by E-quipe.it — Web Agency
                    </span>
                </motion.div>

                {/* Main Title */}
                <motion.h1
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.2 }}
                    className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tight leading-[1.1] mb-6 max-w-5xl mx-auto"
                >
                    Ti creiamo il sito.{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
                        Gratis.
                    </span>
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.4 }}
                    className="text-xl sm:text-3xl font-medium text-gray-200 mb-8 max-w-3xl mx-auto leading-relaxed"
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
                    Siamo E-quipe, agenzia web italiana. Progettiamo il tuo sito professionale a costo zero.
                    Se ti convince, lo pubblichiamo. Se no, nessun problema. Abbiamo anche creato un'app AI per chi preferisce il fai-da-te.
                </motion.p>

                {/* CTA Buttons */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.6 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6 w-full max-w-lg mx-auto mb-12"
                >
                    {/* Primary CTA */}
                    <div className="flex flex-col items-center w-full sm:w-auto">
                        <Link
                            href="https://e-quipe.it"
                            target="_blank"
                            className="group w-full sm:w-auto px-8 py-5 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-bold text-xl transition-all duration-300 transform hover:scale-105 shadow-[0_0_40px_-10px_rgba(37,99,235,0.5)] flex items-center justify-center gap-3 relative overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                            <MessageSquare className="w-6 h-6" />
                            <span>Contattaci — è gratis</span>
                        </Link>
                        <span className="text-xs text-blue-400/80 mt-2 font-medium">
                            Risposta entro 24h
                        </span>
                    </div>

                    {/* Secondary CTA */}
                    <div className="flex flex-col items-center w-full sm:w-auto sm:mt-[-24px]"> {/* Negative margin to align top with primary button ignoring text below */}
                        <a
                            href="#ai-app-hero"
                            onClick={(e) => {
                                e.preventDefault();
                                scrollToNextSection();
                            }}
                            className="w-full sm:w-auto px-6 py-4 text-gray-400 hover:text-white border border-white/10 hover:border-white/30 rounded-full font-medium text-sm transition-all duration-300 flex items-center justify-center gap-2 group"
                        >
                            <span>Oppure prova l'app AI</span>
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </a>
                    </div>
                </motion.div>

                {/* Trust Elements */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.8 }}
                    className="flex flex-wrap justify-center items-center gap-4 sm:gap-8 mb-12 border-t border-white/5 pt-8 w-full max-w-4xl"
                >
                    {["Nessun pagamento anticipato", "Sito professionale su misura", "Paghi solo se sei soddisfatto"].map((text, i) => (
                        <div key={i} className="flex items-center gap-2">
                            <div className="bg-green-500/10 rounded-full p-1">
                                <Check className="w-3 h-3 sm:w-4 sm:h-4 text-green-500" />
                            </div>
                            <span className="text-gray-300 text-xs sm:text-sm font-medium">{text}</span>
                        </div>
                    ))}
                </motion.div>

                {/* Social Proof */}
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={fadeUp}
                    transition={{ duration: 0.7, delay: 0.9 }}
                    className="text-center"
                >
                    <p className="text-gray-500 text-sm">
                        <span className="text-gray-300 font-semibold">Oltre 50 siti creati</span> per attività italiane
                    </p>
                </motion.div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 1 }}
                className="absolute bottom-8 left-1/2 -translate-x-1/2"
            >
                <button
                    onClick={scrollToNextSection}
                    className="text-gray-600 hover:text-white transition-colors animate-bounce p-2"
                >
                    <ChevronDown className="w-8 h-8" />
                </button>
            </motion.div>
        </section>
    );
}
