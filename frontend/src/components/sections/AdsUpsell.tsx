"use client";

import { motion } from "framer-motion";
import { BarChart3, Target, MousePointerClick } from "lucide-react";
import Link from "next/link";

const cards = [
    {
        icon: Target,
        title: "Meta Ads",
        description: "Campagne Instagram e Facebook, targeting avanzato, A/B testing per massimizzare le conversioni."
    },
    {
        icon: MousePointerClick,
        title: "Google Ads",
        description: "Campagne Search e Display, ottimizzazione keyword e bidding automatico per intercettare chi cerca te."
    },
    {
        icon: BarChart3,
        title: "Report Mensile",
        description: "Dashboard con metriche chiare, costo per lead e suggerimenti dell'AI per migliorare costantemente."
    }
];

export default function AdsUpsell() {
    return (
        <section id="ads-service" className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <div className="max-w-4xl mx-auto text-center mb-12">
                    <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">Vuoi anche i clienti? Ci pensiamo noi.</h2>
                    <p className="text-lg text-gray-400">
                        Il nostro team gestisce le tue campagne Meta e Google Ads con il supporto dell'intelligenza artificiale.
                        Tu pensi alla tua attività, noi ti portiamo i clienti.
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-10">
                    {cards.map((card, idx) => {
                        const Icon = card.icon;
                        return (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: idx * 0.1 }}
                                className="bg-[#1a1a2e] p-6 rounded-2xl border border-white/5"
                            >
                                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 text-blue-400">
                                    <Icon className="w-5 h-5" />
                                </div>
                                <h3 className="font-bold text-white mb-2">{card.title}</h3>
                                <p className="text-sm text-gray-400">{card.description}</p>
                            </motion.div>
                        );
                    })}
                </div>

                <div className="text-center">
                    <Link href="#" className="text-blue-400 hover:text-blue-300 text-sm font-medium hover:underline">
                        Scopri di più sul servizio Ads
                    </Link>
                </div>

            </div>
        </section>
    );
}
