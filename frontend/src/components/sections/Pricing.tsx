"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

const plans = [
    {
        name: "Starter",
        price: "€199",
        period: "una tantum",
        description: "Per iniziare",
        features: ["1 pagina", "Sottodominio gratuito", "Certificato SSL", "3 modifiche via chat"],
        highlight: false,
    },
    {
        name: "Business",
        price: "€49",
        period: "/mese",
        description: "Per professionisti",
        features: ["Multi-pagina", "Dominio personalizzato", "Modifiche illimitate", "2 campagne Meta/mese (setup)"],
        highlight: false,
    },
    {
        name: "Growth",
        price: "€99",
        period: "/mese",
        description: "Per crescere veloce",
        features: ["Tutto di Business", "Google Ads inclusi", "5 contenuti AI/mese", "DM automatici", "Report settimanale"],
        highlight: true,
        tag: "CONSIGLIATO"
    },
    {
        name: "Premium",
        price: "€199",
        period: "/mese",
        description: "Tutto incluso",
        features: ["Tutto illimitato", "Account manager dedicato", "Supporto 24/7", "Strategia personalizzata"],
        highlight: false,
    }
];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Pricing() {
    const scrollToForm = () => {
        document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <section id="prezzi" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Prezzi chiari. Nessuna sorpresa.</h2>
                    <p className="text-xl text-gray-400">
                        Il sito te lo creiamo gratis. Paghi solo se decidi di tenerlo online.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-12">
                    {plans.map((plan, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true, margin: "-50px" }}
                            variants={fadeUp}
                            transition={{ duration: 0.4, delay: idx * 0.1 }}
                            className={`relative p-6 rounded-2xl flex flex-col h-full bg-[#16162a] border transition-all ${plan.highlight
                                    ? "border-[#7C3AED] shadow-[0_0_30px_-10px_rgba(124,58,237,0.3)] scale-[1.02] z-10"
                                    : "border-white/5 hover:border-white/20"
                                }`}
                        >
                            {plan.highlight && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#7C3AED] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                    {plan.tag}
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                <p className="text-sm text-gray-400 mb-4">{plan.description}</p>
                                <div className="flex items-baseline">
                                    <span className="text-3xl font-bold text-white tracking-tight">{plan.price}</span>
                                    <span className="text-gray-500 ml-1 text-sm">{plan.period}</span>
                                </div>
                            </div>

                            <ul className="space-y-4 mb-8 flex-grow">
                                {plan.features.map((feat, i) => (
                                    <li key={i} className="flex items-start gap-3">
                                        <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span className="text-sm text-gray-300">{feat}</span>
                                    </li>
                                ))}
                            </ul>

                            <button
                                onClick={scrollToForm}
                                className={`w-full py-3 rounded-xl font-bold text-sm transition-all ${plan.highlight
                                        ? "bg-[#7C3AED] hover:bg-[#6D28D9] text-white shadow-lg"
                                        : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                    }`}
                            >
                                Richiedi il tuo sito
                            </button>
                        </motion.div>
                    ))}
                </div>

                <div className="text-center">
                    <p className="text-sm text-gray-500">* Il budget pubblicitario (da dare a Meta/Google) è separato e lo decidi tu.</p>
                </div>

            </div>
        </section>
    );
}
