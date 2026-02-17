"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Sparkles, ArrowRight, Check } from "lucide-react";

export default function AiHero() {
    return (
        <section className="py-20 lg:py-32 relative overflow-hidden">
            {/* Background Gradient - PURPLE/BLUE for AI feel */}
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(circle at 50% 30%, rgba(124, 58, 237, 0.15) 0%, rgba(0, 0, 0, 0) 70%)",
                }}
            />

            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="mb-8 flex justify-center"
                >
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-sm font-bold tracking-wide backdrop-blur-md">
                        <Sparkles className="w-4 h-4" />
                        Tecnologia AI Proprietaria
                    </span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="text-5xl lg:text-7xl font-extrabold text-white mb-6 leading-tight max-w-4xl mx-auto"
                >
                    Il tuo sito professionale <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-500">
                        in 60 secondi.
                    </span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto"
                >
                    Niente codice. Niente drag & drop complicati.
                    Rispondi a 3 domande e la nostra AI costruisce tutto per te.
                    Testi, immagini e design inclusi.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20"
                >
                    <Link href="/auth">
                        <button className="px-10 py-4 bg-white text-black rounded-xl font-bold text-lg hover:scale-105 transition-transform shadow-[0_0_40px_-5px_rgba(255,255,255,0.3)] flex items-center gap-2">
                            Prova Gratis l'App
                            <ArrowRight className="w-5 h-5" />
                        </button>
                    </Link>
                </motion.div>

                {/* App Interface Visual Placeholder */}
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="relative max-w-5xl mx-auto rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-[#0f0f1a] aspect-[16/9] group"
                >
                    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
                        <div className="text-center">
                            <Sparkles className="w-16 h-16 text-purple-500 mx-auto mb-4 opacity-50" />
                            <p className="text-white/40 font-mono text-sm uppercase tracking-widest">[APP INTERFACE PREVIEW - Generazione Immagine]</p>
                        </div>
                    </div>

                    {/* Steps Overlay */}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-md border-t border-white/10 p-6 grid grid-cols-3 gap-4">
                        <div className="flex flex-col items-center">
                            <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold mb-2">1</div>
                            <p className="text-xs text-gray-400">Inserisci il nome</p>
                        </div>
                        <div className="flex flex-col items-center">
                            <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold mb-2">2</div>
                            <p className="text-xs text-gray-400">Scegli lo stile</p>
                        </div>
                        <div className="flex flex-col items-center">
                            <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold mb-2">3</div>
                            <p className="text-xs text-gray-400">Sito Pronto</p>
                        </div>
                    </div>
                </motion.div>

            </div>
        </section>
    );
}
