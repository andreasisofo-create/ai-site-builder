"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function AiBuilderSection() {
    return (
        <section id="ai-builder" className="py-20 bg-[#1a1a2e] border-y border-white/5">
            <div className="container mx-auto px-6">
                <div className="flex flex-col lg:flex-row items-center gap-12 max-w-6xl mx-auto">
                    <div className="flex-1 space-y-6 text-center lg:text-left">
                        <h2 className="text-3xl font-bold text-white">Preferisci fare da solo? <br />Prova la nostra app.</h2>
                        <p className="text-gray-300 text-lg leading-relaxed">
                            Con il nostro builder AI, puoi creare il tuo sito in 60 secondi.
                            Descrivi la tua attività, scegli uno stile, e l'intelligenza artificiale fa il resto.
                        </p>
                        <div className="pt-2">
                            <Link
                                href="/auth"
                                className="inline-flex items-center gap-2 px-8 py-3 rounded-full border border-white/20 hover:border-white/50 text-white font-medium hover:bg-white/5 transition-all group"
                            >
                                Provalo gratis
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </Link>
                        </div>
                    </div>

                    <div className="flex-1 w-full max-w-md lg:max-w-none">
                        <div className="relative aspect-video bg-black/40 rounded-xl overflow-hidden border border-white/10 shadow-2xl">
                            {/* Placeholder for App Screenshot */}
                            <div className="absolute inset-0 flex items-center justify-center text-gray-500 bg-gradient-to-br from-[#2a2a40] to-[#1a1a2e]">
                                <span className="text-sm font-mono">[AI App Interface Screenshot]</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
