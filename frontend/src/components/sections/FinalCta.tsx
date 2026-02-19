"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

export default function FinalCta() {
    const { language } = useLanguage();
    const txt = translations[language].finalCta;

    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

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
                    className="text-xl text-white/90 mb-10 font-medium"
                >
                    {txt.subtitle}
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.15 }}
                    className="mb-8"
                >
                    <a href="https://www.e-quipe.it" target="_blank" rel="noopener noreferrer" className="inline-block">
                        <div className="relative w-36 h-10 mx-auto opacity-90 hover:opacity-100 transition-opacity">
                            <Image src="/logo.png" alt="E-quipe" fill className="object-contain" />
                        </div>
                    </a>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6"
                >
                    <a
                        href="https://www.e-quipe.it/it"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-8 py-4 bg-white text-[#0090FF] rounded-full font-bold text-lg hover:bg-gray-100 transition-colors shadow-xl inline-block"
                    >
                        Entra in E-quipe
                    </a>

                    <Link
                        href="/auth"
                        className="flex items-center gap-2 text-white font-semibold hover:text-white/80 transition-colors group"
                    >
                        {txt.ctaSecondary} <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </motion.div>
            </div>
        </section>
    );
}
