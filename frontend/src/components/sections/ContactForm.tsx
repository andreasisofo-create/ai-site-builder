"use client";

import { motion } from "framer-motion";
import { Lock, Send } from "lucide-react";
import { useState } from "react";
import { useLanguage, translations } from "@/lib/i18n";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function ContactForm() {
    const { language } = useLanguage();
    const txt = translations[language].contact;
    const [submitted, setSubmitted] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        const formData = new FormData(e.currentTarget);

        try {
            const res = await fetch("https://api.web3forms.com/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    access_key: "4e402f7c-7121-41b8-b80a-82d2306a548a",
                    subject: "Nuova richiesta sito da landing page",
                    from_name: "E-quipe Landing Page",
                    name: formData.get("name"),
                    activity: formData.get("activity"),
                    contact: formData.get("contact"),
                    has_site: formData.get("hasSite"),
                }),
            });

            if (res.ok) {
                setSubmitted(true);
            }
        } catch {
            // fallback: still show success (form data was attempted)
            setSubmitted(true);
        } finally {
            setLoading(false);
        }
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
                        {txt.title}
                    </motion.h2>
                    <motion.p
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={fadeUp}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-gray-300"
                    >
                        {txt.subtitle}
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
                            <h3 className="text-2xl font-bold text-white mb-2">{txt.successTitle}</h3>
                            <p className="text-gray-300">{txt.successMessage}</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">{txt.nameLabel}</label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    required
                                    placeholder={txt.namePlaceholder}
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="activity" className="block text-sm font-medium text-gray-300 mb-2">{txt.activityLabel}</label>
                                <input
                                    type="text"
                                    id="activity"
                                    name="activity"
                                    required
                                    placeholder={txt.activityPlaceholder}
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="contact" className="block text-sm font-medium text-gray-300 mb-2">{txt.contactLabel}</label>
                                <input
                                    type="text"
                                    id="contact"
                                    name="contact"
                                    required
                                    placeholder={txt.contactPlaceholder}
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label htmlFor="hasSite" className="block text-sm font-medium text-gray-300 mb-2">{txt.hasSiteLabel}</label>
                                <select
                                    id="hasSite"
                                    name="hasSite"
                                    className="w-full px-4 py-3 bg-[#0a0a1a] border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-[#0090FF] focus:border-transparent transition-all"
                                >
                                    <option value="no">{txt.hasSiteNo}</option>
                                    <option value="yes">{txt.hasSiteYes}</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-4 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? txt.loading : txt.submit}
                            </button>

                            <div className="flex items-center justify-center gap-2 text-xs text-gray-500 mt-4">
                                <Lock className="w-3 h-3" />
                                <span>{txt.privacy}</span>
                            </div>
                        </form>
                    )}

                    {!submitted && (
                        <div className="mt-8 pt-6 border-t border-white/10 text-center">
                            <a href="https://wa.me/393899094183" className="text-sm text-gray-400 hover:text-white transition-colors flex items-center justify-center gap-2">
                                {txt.whatsapp} <span className="underline decoration-[#25D366] underline-offset-4">{txt.whatsappLink}</span>
                            </a>
                        </div>
                    )}
                </motion.div>
            </div>
        </section>
    );
}
