"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function SocialProof() {
    const { language } = useLanguage();
    const reviews = translations[language].reviews;

    return (
        <section className="py-20 bg-[#0f0f23] border-b border-white/5">
            <div className="container mx-auto px-6">
                <div className="grid md:grid-cols-3 gap-8">
                    {reviews.map((review, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                            transition={{ delay: idx * 0.1 }}
                            className="bg-[#16162a] p-8 rounded-2xl border border-white/5"
                        >
                            <div className="flex gap-1 mb-4">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} className="w-5 h-5 text-[#0090FF] fill-[#0090FF]" />
                                ))}
                            </div>
                            <p className="text-gray-300 mb-6 italic">&ldquo;{review.text}&rdquo;</p>
                            <div>
                                <p className="text-white font-bold">{review.name}</p>
                                <p className="text-[#0090FF] text-sm">{review.role}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>

            </div>
        </section>
    );
}
