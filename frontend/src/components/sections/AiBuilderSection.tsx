"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Sparkles } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

export default function AiBuilderSection() {
    const { language } = useLanguage();
    const txt = translations[language].aiBuilder;

    return (
        <section className="py-24 relative overflow-hidden bg-[#0a1628]">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-[#0090FF]/15 via-transparent to-transparent opacity-60 pointer-events-none" />

            <div className="container mx-auto px-6 relative z-10">
                <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">

                    <div className="lg:w-1/2">
                        <motion.div
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0090FF]/10 border border-[#0090FF]/30 text-[#0090FF] text-xs uppercase font-bold tracking-widest mb-6">
                                <Sparkles className="w-3 h-3" />
                                {txt.badge}
                            </div>
                            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                                {txt.title} <br />
                                {txt.titleLine2}
                            </h2>
                            {/* Blue stripe separator */}
                            <div className="w-24 h-1 bg-gradient-to-r from-[#0090FF] to-[#0050CC] rounded-full mb-6" />
                            <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                                {txt.description}
                            </p>

                            <Link href="/auth">
                                <button className="px-8 py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all flex items-center gap-2 shadow-lg shadow-blue-900/40">
                                    {txt.cta}
                                    <Sparkles className="w-4 h-4" />
                                </button>
                            </Link>
                        </motion.div>
                    </div>

                    <div className="lg:w-1/2 relative">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            className="relative aspect-square max-w-md mx-auto"
                        >
                            {/* Abstract Visual Representation of AI Builder */}
                            <div className="absolute inset-0 bg-gradient-to-tr from-purple-600/20 to-blue-600/20 rounded-full blur-3xl" />
                            <div className="relative bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 shadow-2xl h-full flex flex-col">
                                <div className="w-full h-8 bg-white/5 rounded-lg mb-4 flex items-center px-4 gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-500" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                    <div className="w-3 h-3 rounded-full bg-green-500" />
                                </div>
                                <div className="flex-grow bg-white/5 rounded-xl flex items-center justify-center relative overflow-hidden group">
                                    <span className="text-white/20 font-mono">AI GENERATING...</span>
                                    <div className="absolute inset-0 bg-gradient-to-t from-purple-900/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                                </div>
                                <div className="mt-4 h-4 w-3/4 bg-white/10 rounded-full" />
                                <div className="mt-2 h-4 w-1/2 bg-white/10 rounded-full" />
                            </div>

                            {/* Floating Elements */}
                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                className="absolute -top-6 -right-6 bg-[#0f0f23] border border-white/20 p-4 rounded-xl shadow-xl"
                            >
                                <span className="text-green-400 font-bold text-sm">{txt.floatingBadge1}</span>
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, 10, 0] }}
                                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                                className="absolute -bottom-6 -left-6 bg-[#0f0f23] border border-white/20 p-4 rounded-xl shadow-xl"
                            >
                                <span className="text-blue-400 font-bold text-sm">{txt.floatingBadge2}</span>
                            </motion.div>
                        </motion.div>
                    </div>

                </div>
            </div>
        </section>
    );
}
