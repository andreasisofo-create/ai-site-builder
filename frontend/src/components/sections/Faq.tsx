"use client";

import { motion } from "framer-motion";
import { Plus, Minus } from "lucide-react";
import { useState } from "react";
import { useLanguage, translations } from "@/lib/i18n";

export default function Faq() {
    const { language } = useLanguage();
    const txt = translations[language].faqAgency;
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section id="faq" className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6 max-w-3xl">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-white mb-4">{txt.title}</h2>
                </div>

                <div className="space-y-4">
                    {txt.items.map((faq, idx) => (
                        <div
                            key={idx}
                            className="bg-[#16162a] border border-white/5 rounded-2xl overflow-hidden transition-all hover:border-white/10"
                        >
                            <button
                                onClick={() => setOpenIndex(idx === openIndex ? null : idx)}
                                className="w-full text-left p-6 flex items-center justify-between"
                            >
                                <span className="font-bold text-white text-lg">{faq.q}</span>
                                {openIndex === idx ? (
                                    <Minus className="w-5 h-5 text-[#0090FF]" />
                                ) : (
                                    <Plus className="w-5 h-5 text-[#0090FF]" />
                                )}
                            </button>
                            <motion.div
                                initial={false}
                                animate={{ height: openIndex === idx ? "auto" : 0, opacity: openIndex === idx ? 1 : 0 }}
                                transition={{ duration: 0.3 }}
                                className="overflow-hidden"
                            >
                                <div className="p-6 pt-0 text-gray-400">
                                    {faq.a}
                                </div>
                            </motion.div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
