"use client";

import { motion } from "framer-motion";
import { Megaphone, TrendingUp, Target } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

export default function AdsUpsell() {
    const { language } = useLanguage();
    const txt = translations[language].adsUpsell;

    return (
        <section className="py-20 bg-[#0a0a1a] relative overflow-hidden">
            {/* Background blobs */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#0090FF]/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-[#0090FF]/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="container mx-auto px-6 relative z-10">
                <div className="max-w-4xl mx-auto bg-gradient-to-br from-[#16162a] to-[#0f0f1a] border border-[#0090FF]/20 rounded-3xl p-8 lg:p-12 text-center shadow-[0_0_50px_-20px_rgba(0,144,255,0.15)]">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <div className="w-16 h-16 bg-[#0090FF]/10 text-[#0090FF] rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <Megaphone className="w-8 h-8" />
                        </div>

                        <h2 className="text-3xl font-bold text-white mb-4">{txt.title}</h2>
                        <p className="text-gray-400 mb-10 max-w-2xl mx-auto">
                            {txt.description}
                        </p>

                        <div className="grid sm:grid-cols-3 gap-6 mb-10 text-left">
                            <div className="bg-[#0a0a1a] p-5 rounded-xl border border-white/5">
                                <Target className="w-6 h-6 text-[#0090FF] mb-3" />
                                <h3 className="font-bold text-white mb-1">{txt.feature1Title}</h3>
                                <p className="text-xs text-gray-500">{txt.feature1Desc}</p>
                            </div>
                            <div className="bg-[#0a0a1a] p-5 rounded-xl border border-white/5">
                                <TrendingUp className="w-6 h-6 text-[#0090FF] mb-3" />
                                <h3 className="font-bold text-white mb-1">{txt.feature2Title}</h3>
                                <p className="text-xs text-gray-500">{txt.feature2Desc}</p>
                            </div>
                            <div className="bg-[#0a0a1a] p-5 rounded-xl border border-white/5">
                                <Megaphone className="w-6 h-6 text-[#0090FF] mb-3" />
                                <h3 className="font-bold text-white mb-1">{txt.feature3Title}</h3>
                                <p className="text-xs text-gray-500">{txt.feature3Desc}</p>
                            </div>
                        </div>

                        <a href="/ads" className="inline-block px-8 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-blue-900/30">
                            {txt.cta}
                        </a>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
