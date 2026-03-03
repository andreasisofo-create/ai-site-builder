"use client";

import { motion } from "framer-motion";
import { Mic, MessageCircle, Volume2 } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

function AudioWave() {
    return (
        <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
                <motion.div
                    key={i}
                    className="w-1 bg-[#0090FF] rounded-full"
                    animate={{
                        height: [8, 20 + Math.random() * 12, 8],
                    }}
                    transition={{
                        duration: 0.8 + Math.random() * 0.4,
                        repeat: Infinity,
                        delay: i * 0.1,
                        ease: "easeInOut",
                    }}
                />
            ))}
        </div>
    );
}

export default function VoiceAssistant() {
    const { language } = useLanguage();
    const txt = translations[language].voiceAssistant;

    return (
        <section className="py-24 relative overflow-hidden bg-[#0a1628]">
            <div
                className="absolute inset-0 z-0 pointer-events-none"
                style={{
                    background: "radial-gradient(ellipse at 70% 50%, rgba(0, 144, 255, 0.10) 0%, rgba(0, 0, 0, 0) 60%)",
                }}
            />

            <div className="container mx-auto px-6 relative z-10">
                <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20 max-w-6xl mx-auto">

                    {/* Left — Text */}
                    <div className="lg:w-1/2">
                        <motion.div
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                        >
                            {/* Badge */}
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 text-xs uppercase font-bold tracking-widest mb-6">
                                <Mic className="w-3 h-3" />
                                {txt.badge}
                            </span>

                            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4 leading-tight">
                                {txt.title}
                            </h2>

                            <div className="w-24 h-1 bg-gradient-to-r from-[#0090FF] to-[#0050CC] rounded-full mb-6" />

                            <p className="text-gray-400 text-lg mb-2 leading-relaxed">
                                {txt.description}
                            </p>
                            <p className="text-white font-semibold text-lg mb-8">
                                {txt.punchline}
                            </p>

                            {/* CTAs */}
                            <div className="flex flex-col sm:flex-row gap-4">
                                <a
                                    href="https://www.e-quipe.it"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-8 py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-900/40"
                                >
                                    <Volume2 className="w-5 h-5" />
                                    {txt.cta}
                                </a>
                                <a
                                    href="https://wa.me/393899094183"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-8 py-4 bg-[#25D366]/10 hover:bg-[#25D366]/20 text-[#25D366] border border-[#25D366]/30 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2"
                                >
                                    <MessageCircle className="w-5 h-5" />
                                    {txt.ctaSecondary}
                                </a>
                            </div>
                        </motion.div>
                    </div>

                    {/* Right — Chat Mockup */}
                    <div className="lg:w-1/2">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="relative max-w-md mx-auto"
                        >
                            <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl p-6 shadow-2xl">
                                {/* Chat header */}
                                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5">
                                    <div className="w-10 h-10 rounded-full bg-[#0090FF]/20 flex items-center justify-center">
                                        <Mic className="w-5 h-5 text-[#0090FF]" />
                                    </div>
                                    <div>
                                        <p className="text-white font-semibold text-sm">Assistente AI</p>
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-2 h-2 rounded-full bg-green-500" />
                                            <span className="text-green-400 text-xs">Online</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Chat messages */}
                                <div className="space-y-4">
                                    {txt.chatMessages.map((msg, idx) => (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, y: 10 }}
                                            whileInView={{ opacity: 1, y: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ delay: 0.4 + idx * 0.3 }}
                                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                                        >
                                            <div
                                                className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm ${
                                                    msg.role === "user"
                                                        ? "bg-[#0090FF] text-white rounded-br-md"
                                                        : "bg-white/5 text-gray-300 rounded-bl-md"
                                                }`}
                                            >
                                                {msg.text}
                                                {msg.role === "assistant" && (
                                                    <div className="mt-2 flex items-center gap-2">
                                                        <Volume2 className="w-3.5 h-3.5 text-[#0090FF]" />
                                                        <AudioWave />
                                                    </div>
                                                )}
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>

                            {/* Floating glow */}
                            <div className="absolute -inset-4 bg-[#0090FF]/5 rounded-3xl blur-2xl -z-10" />
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
}
