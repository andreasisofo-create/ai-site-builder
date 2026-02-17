"use client";

import { motion } from "framer-motion";
import { Lock, Send } from "lucide-react";
import { useState } from "react";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function ContactForm() {
    const [submitted, setSubmitted] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        // Simulate API call
        setTimeout(() => {
            setLoading(false);
            setSubmitted(true);
        }, 1500);
    };

    return (
        <section
            id="form-contatto"
            className="py-20 lg:py-28 relative overflow-hidden"
        >
            {/* Special Gradient Background - BLUE */}
            <div
                className="absolute inset-0 z-0"
                style={{
                    background: "linear-gradient(135deg, #1a1a3e 0%, #0f0f23 100%)"
                }}
            />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/40 via-transparent to-transparent opacity-50 pointer-events-none" />

            <div className="container mx-auto px-6 relative z-10">
                <div className="max-w-2xl mx-auto text-center mb-12">
                    <motion.h2
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={fadeUp}
                        className="text-3xl lg:text-5xl font-bold text-white mb-4"
                    >
                        Raccontaci la tua attività
                    </motion.h2>
                    <motion.p
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={fadeUp}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-gray-300"
                    >
                        Ti creiamo il sito gratis. Senza impegno.
                    </motion.p>
                </div>

                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    transition={{ delay: 0.2 }}
                    className="max-w-xl mx-auto bg-[#1a1a2e]/80 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative"
                >
                    {/* Glow Effect around form - BLUE */}
                    <div className="absolute -inset-1 bg-gradient-to-r from-[#0090FF] to-[#3B82F6] rounded-2xl opacity-20 blur-lg -z-10" />

                    {submitted ? (
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-6">
                                <Send className="w-8 h-8 text-green-500" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-2">Richiesta Ricevuta!</h3>
                            <p className="text-gray-300">Grazie per averci contattato. Il nostro team analizzerà la tua richiesta e ti risponderà entro 24 ore.</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">Nome</label>
                                <input
                                    type="text"
                                    id="name"
                                    required
                                    placeholder="Il tuo nome"
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="activity" className="block text-sm font-medium text-gray-300 mb-2">Attività</label>
                                <input
                                    type="text"
                                    id="activity"
                                    required
                                    placeholder="Che attività hai? (es: ristorante, studio legale...)"
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="contact" className="block text-sm font-medium text-gray-300 mb-2">Contatto</label>
                                <input
                                    type="text"
                                    id="contact"
                                    required
                                    placeholder="Email o numero di telefono"
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="hasSite" className="block text-sm font-medium text-gray-300 mb-2">Hai già un sito?</label>
                                <select
                                    id="hasSite"
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                >
                                    <option value="no">No, è il primo sito</option>
                                    <option value="yes">Sì, voglio rifarlo</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? "Invio in corso..." : "Voglio il mio sito gratis"}
                            </button>

                            <div className="flex items-center justify-center gap-2 text-xs text-gray-500 mt-4">
                                <Lock className="w-3 h-3" />
                                <span>I tuoi dati sono al sicuro. Nessun impegno.</span>
                            </div>
                        </form>
                    )}

                    {!submitted && (
                        <div className="mt-8 pt-6 border-t border-white/10 text-center">
                            <a href="https://wa.me/390000000000" className="text-sm text-gray-400 hover:text-white transition-colors flex items-center justify-center gap-2">
                                Preferisci WhatsApp? <span className="underline decoration-[#25D366] underline-offset-4">Scrivici qui →</span>
                            </a>
                        </div>
                    )}
                </motion.div>
            </div>
        </section>
    );
}
