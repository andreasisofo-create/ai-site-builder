"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Check } from "lucide-react";

const plans = [
    {
        name: "Pack Presenza",
        slug: "pack-presenza",
        price: "\u20AC499",
        setup: "una tantum",
        subscription: "+ \u20AC39/mese",
        description: "Per chi vuole essere online con un sito professionale.",
        features: [
            "Homepage AI completa",
            "3 pagine extra incluse (4 totali)",
            "Dominio personalizzato (1\u00B0 anno)",
            "Hosting + SSL + Backup",
            "Modifiche illimitate via chat"
        ],
        highlight: false,
    },
    {
        name: "Pack Clienti",
        slug: "pack-clienti",
        price: "\u20AC499",
        setup: "una tantum",
        subscription: "+ \u20AC199/mese",
        description: "Per iniziare subito a ricevere clienti da Instagram e Facebook.",
        features: [
            "Tutto del Pack Presenza",
            "Meta Ads (Instagram & Facebook)",
            "Contenuti Base (8 post AI/mese)",
            "Report mensile performance",
            "Supporto via chat"
        ],
        highlight: false,
    },
    {
        name: "Pack Crescita",
        slug: "pack-crescita",
        price: "\u20AC499",
        setup: "SETUP GRATUITO",
        subscription: "+ \u20AC399/mese",
        description: "Per crescere seriamente con Google e Meta insieme.",
        features: [
            "Sito Web Custom completo (8 pagine)",
            "Dominio personalizzato incluso",
            "Full Ads: Meta Pro + Google Ads",
            "DM automatici ai lead",
            "Contenuti Pro (illimitati)",
            "Report settimanale dettagliato",
            "Manutenzione inclusa",
            "Supporto prioritario"
        ],
        highlight: true,
        tag: "CONSIGLIATO"
    },
    {
        name: "Pack Premium",
        slug: "pack-premium",
        price: "\u20AC1.499",
        setup: "SETUP GRATUITO",
        subscription: "+ \u20AC999/mese",
        description: "Per attivita' ambiziose. Un'agenzia digitale dedicata.",
        features: [
            "Tutto del Pack Crescita",
            "Pagine sito illimitate",
            "Campagne illimitate su tutti i canali",
            "Account manager dedicato",
            "Strategia marketing mensile",
            "Report personalizzato e call mensile",
            "Supporto 24/7 dedicato"
        ],
        highlight: false,
    }
];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Pricing() {
    const router = useRouter();

    const handleCheckout = (slug: string) => {
        router.push(`/checkout?service=${slug}`);
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
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Pack Completi</h2>
                    <p className="text-xl text-gray-400">
                        Soluzioni tutto-incluso con risparmio garantito.
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
                                    ? "border-[#0090FF] shadow-[0_0_30px_-10px_rgba(0,144,255,0.3)] scale-[1.02] z-10"
                                    : "border-white/5 hover:border-white/20"
                                }`}
                        >
                            {plan.highlight && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#0090FF] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                    {plan.tag}
                                </div>
                            )}

                            <div className="mb-6">
                                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                <p className="text-sm text-gray-400 mb-4 h-10">{plan.description}</p>
                                <div className="flex flex-col">
                                    <div className="flex items-baseline">
                                        <span className="text-3xl font-bold text-white tracking-tight">{plan.price}</span>
                                        <span className="text-gray-500 ml-1 text-sm">{plan.subscription}</span>
                                    </div>
                                    <span className="text-xs text-[#0090FF] font-semibold uppercase tracking-wide mt-1">{plan.setup}</span>
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
                                onClick={() => handleCheckout(plan.slug)}
                                className={`w-full py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${plan.highlight
                                        ? "bg-[#0090FF] hover:bg-[#0070C9] text-white shadow-lg"
                                        : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                    }`}
                            >
                                {`Scegli ${plan.name}`}
                            </button>
                        </motion.div>
                    ))}
                </div>

                <div className="text-center">
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5 mx-2">
                        * Budget pubblicitario esclusi
                    </span>
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5 mx-2">
                        ** Sconto 15% pagamento annuale
                    </span>
                </div>

            </div>
        </section>
    );
}
