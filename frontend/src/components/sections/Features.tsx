"use client";

import { motion } from "framer-motion";
import { Smartphone, PenTool, Server, Search, MessageSquare, Layout } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const icons = [Layout, Smartphone, PenTool, Server, Search, MessageSquare];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Features() {
    const { language } = useLanguage();
    const txt = translations[language].featuresAgency;

    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <section id="funzionalita" className="py-20 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">{txt.title}</h2>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto mb-16">
                    {txt.items.map((feat, idx) => {
                        const Icon = icons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden"
                                whileInView="visible"
                                viewport={{ once: true, margin: "-50px" }}
                                variants={fadeUp}
                                transition={{ duration: 0.4, delay: idx * 0.1 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:bg-[#1a1a2e] transition-colors"
                            >
                                <div className="w-12 h-12 rounded-lg bg-[#0090FF]/10 flex items-center justify-center mb-4 text-[#0090FF]">
                                    <Icon className="w-6 h-6" />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-2">{feat.title}</h3>
                                <p className="text-gray-400 text-sm">{feat.description}</p>
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
                        className="px-8 py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all shadow-lg hover:-translate-y-0.5"
                    >
                        {txt.cta}
                    </button>
                </motion.div>

            </div>
        </section>
    );
}
