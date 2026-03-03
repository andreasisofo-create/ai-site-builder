"use client";

import { motion } from "framer-motion";
import { Volume2, MessageCircle } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

export default function FinalCta() {
    const { language } = useLanguage();
    const txt = translations[language].finalCta;

    return (
        <section className="py-24 relative overflow-hidden">
            {/* Bold Gradient Background - BLUE */}
            <div
                className="absolute inset-0 z-0"
                style={{
                    background: "linear-gradient(135deg, #0090FF 0%, #1e40af 100%)"
                }}
            />

            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-3xl lg:text-5xl font-extrabold text-white mb-6 tracking-tight"
                >
                    {txt.title}
                </motion.h2>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="text-xl text-white/90 mb-10 font-medium max-w-2xl mx-auto"
                >
                    {txt.subtitle}
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6"
                >
                    <a
                        href="https://www.e-quipe.it"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-8 py-4 bg-white text-[#0090FF] rounded-full font-bold text-lg hover:bg-gray-100 transition-colors shadow-xl inline-flex items-center gap-2"
                    >
                        <Volume2 className="w-5 h-5" />
                        {txt.cta}
                    </a>

                    <a
                        href="https://wa.me/393899094183"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-white font-semibold hover:text-white/80 transition-colors group px-6 py-3 bg-white/10 rounded-full border border-white/20"
                    >
                        <MessageCircle className="w-5 h-5" />
                        {txt.ctaSecondary}
                    </a>
                </motion.div>
            </div>
        </section>
    );
}
