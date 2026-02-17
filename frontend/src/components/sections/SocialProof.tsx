"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";
import Image from "next/image";

const testimonials = [
    {
        name: "Marco R.",
        role: "Proprietario",
        activity: "Ristorante Da Mario, Roma",
        quote: "Ho creato il sito in pausa pranzo. Il giorno dopo avevo già ricevuto due richieste di prenotazione.",
        image: "/avatars/marco.webp", // Placeholder
    },
    {
        name: "Laura B.",
        role: "Avvocato",
        activity: "Studio Legale, Milano",
        quote: "Non avevo mai avuto un sito. In 10 minuti ero online con un risultato che sembra fatto da un'agenzia.",
        image: "/avatars/laura.webp", // Placeholder
    },
    {
        name: "Giuseppe V.",
        role: "Titolare",
        activity: "Idraulico, Torino",
        quote: "Le campagne Google mi portano 10 contatti a settimana. Ho dovuto assumere un'altra persona.",
        image: "/avatars/giuseppe.webp", // Placeholder
    },
];

const fadeUp = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0 },
};

export default function SocialProof() {
    return (
        <section id="social-proof" className="py-20 bg-[#0f0f23] relative overflow-hidden">
            {/* Background Gradient */}
            <div
                className="absolute inset-0 z-0 opacity-30"
                style={{
                    background: "radial-gradient(circle at 50% 50%, rgba(124, 58, 237, 0.1) 0%, transparent 60%)"
                }}
            />

            <div className="container mx-auto px-6 relative z-10">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    variants={fadeUp}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-12"
                >
                    <h2 className="text-sm font-bold uppercase tracking-widest text-gray-400 mb-2">Hanno scelto E-quipe</h2>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {testimonials.map((t, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true, margin: "-50px" }}
                            variants={fadeUp}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="bg-[#1a1a2e] rounded-2xl p-6 border border-white/5 hover:border-[#7C3AED]/30 transition-all hover:-translate-y-1 shadow-lg"
                        >
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center text-lg font-bold text-white border border-white/10">
                                    {t.name.charAt(0)}
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">{t.name}</h3>
                                    <p className="text-xs text-gray-400">{t.activity}</p>
                                </div>
                            </div>

                            <div className="flex gap-1 mb-3">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                ))}
                            </div>

                            <p className="text-gray-300 text-sm italic leading-relaxed">
                                "{t.quote}"
                            </p>
                        </motion.div>
                    ))}
                </div>

                {/* Stats Bar */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                    className="mt-16 pt-8 border-t border-white/5 flex flex-wrap justify-center gap-8 md:gap-16 text-center"
                >
                    <div>
                        <p className="text-2xl md:text-3xl font-bold text-white">200+</p>
                        <p className="text-xs uppercase tracking-wider text-gray-500">Siti Online</p>
                    </div>
                    <div>
                        <p className="text-2xl md:text-3xl font-bold text-white">4.8/5</p>
                        <p className="text-xs uppercase tracking-wider text-gray-500">Valutazione</p>
                    </div>
                    <div>
                        <p className="text-2xl md:text-3xl font-bold text-white">24h</p>
                        <p className="text-xs uppercase tracking-wider text-gray-500">Tempo Risposta</p>
                    </div>
                </motion.div>

            </div>
        </section>
    );
}
