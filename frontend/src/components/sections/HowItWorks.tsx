"use client";

import { motion } from "framer-motion";
import { MessageSquare, Layout, ThumbsUp } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const icons = [MessageSquare, Layout, ThumbsUp];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function HowItWorks() {
    const { language } = useLanguage();
    const txt = translations[language].howItWorksAgency;

    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <section id="come-funziona" className="py-20 lg:py-28 bg-[#0a0a1a] relative">
            <div className="container mx-auto px-6">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    variants={fadeUp}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">{txt.title}</h2>
                    <p className="text-xl text-gray-400">{txt.subtitle}</p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
                    {txt.steps.map((step, idx) => {
                        const Icon = icons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden"
                                whileInView="visible"
                                viewport={{ once: true, margin: "-50px" }}
                                variants={fadeUp}
                                transition={{ duration: 0.5, delay: idx * 0.2 }}
                                className="bg-[#16162a] rounded-2xl p-8 border border-white/5 relative group hover:border-[#0090FF]/30 transition-colors"
                            >
                                {/* Number Watermark */}
                                <span className="absolute top-4 right-6 text-6xl font-black text-white/5 pointer-events-none group-hover:text-white/10 transition-colors">
                                    0{idx + 1}
                                </span>

                                <div className="w-14 h-14 rounded-xl bg-[#0090FF]/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                    <Icon className="w-7 h-7 text-[#0090FF]" />
                                </div>

                                <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                                <p className="text-gray-400 leading-relaxed">{step.description}</p>
                            </motion.div>
                        );
                    })}
                </div>

                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center"
                >
                    <button
                        onClick={scrollToForm}
                        className="px-8 py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all shadow-[0_4px_14px_0_rgba(0,144,255,0.39)] hover:shadow-[0_6px_20px_rgba(0,144,255,0.23)] hover:-translate-y-0.5"
                    >
                        {txt.cta}
                    </button>
                </motion.div>
            </div>
        </section>
    );
}
