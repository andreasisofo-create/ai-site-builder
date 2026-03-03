"use client";

import { motion } from "framer-motion";
import { Bot, Search, Brain } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const cardIcons = [Bot, Search, Brain];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function AiRevolution() {
    const { language } = useLanguage();
    const txt = translations[language].aiRevolution;

    return (
        <section className="py-24 relative overflow-hidden bg-[#0f0f23]">
            {/* Urgent gradient — warm red/orange */}
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(ellipse at 50% 0%, rgba(239, 68, 68, 0.12) 0%, rgba(0, 0, 0, 0) 60%)",
                }}
            />

            <div className="container mx-auto px-6 relative z-10 max-w-4xl">
                {/* Badge */}
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-6"
                >
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs uppercase font-bold tracking-widest">
                        {txt.badge}
                    </span>
                </motion.div>

                {/* Headline */}
                <motion.h2
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    transition={{ delay: 0.1 }}
                    className="text-3xl lg:text-5xl font-extrabold text-white text-center mb-6 tracking-tight"
                >
                    {txt.title}
                </motion.h2>

                {/* Body */}
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    transition={{ delay: 0.2 }}
                    className="text-center mb-12"
                >
                    <p className="text-lg text-gray-400 mb-2">{txt.description}</p>
                    <p className="text-xl font-semibold text-orange-400 italic mb-4">{txt.query}</p>
                    <p className="text-lg text-gray-300 font-medium">{txt.punchline}</p>
                </motion.div>

                {/* 3 AI Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl mx-auto">
                    {txt.cards.map((card, idx) => {
                        const Icon = cardIcons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden"
                                whileInView="visible"
                                viewport={{ once: true, margin: "-30px" }}
                                variants={fadeUp}
                                transition={{ duration: 0.4, delay: 0.3 + idx * 0.1 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5 text-center hover:border-red-500/20 transition-colors"
                            >
                                <div className="w-14 h-14 rounded-xl bg-red-500/10 flex items-center justify-center mx-auto mb-4">
                                    <Icon className="w-7 h-7 text-red-400" />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-1">{card.name}</h3>
                                <p className="text-sm text-gray-400">{card.description}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}
