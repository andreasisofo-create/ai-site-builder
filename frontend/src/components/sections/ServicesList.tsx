"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Megaphone, Building2 } from "lucide-react";

const serviceCategories = [
    {
        icon: Sparkles,
        name: "AI Builder",
        subtitle: "Crei il sito da solo con l\u2019AI",
        color: "#0090FF",
        items: [
            { label: "Prova Gratuita", price: "Gratis", note: "" },
            { label: "Starter (5 pagine, sottodominio)", price: "\u20AC19,90", note: "/mese" },
            { label: "Pro (15 pagine, dominio .it/.com)", price: "\u20AC39", note: "/mese" },
        ],
        cta: "Prova Gratis",
        link: "/dashboard",
    },
    {
        icon: Megaphone,
        name: "Pack Ads",
        subtitle: "Campagne Meta e Google gestite",
        color: "#22C55E",
        items: [
            { label: "Meta Ads (Base / Pro / Elite)", price: "da \u20AC199", note: "/mese + % budget" },
            { label: "Google Ads (Base / Pro / Elite)", price: "da \u20AC249", note: "/mese + % budget" },
            { label: "Combo Meta + Google", price: "da \u20AC379", note: "/mese + % budget" },
        ],
        cta: "Scopri Pack Ads",
        link: "/ads#prezzi-ads",
    },
    {
        icon: Building2,
        name: "Sito Su Misura",
        subtitle: "Il nostro team crea il tuo sito",
        color: "#A855F7",
        items: [
            { label: "Homepage (design personalizzato)", price: "\u20AC349", note: "una tantum" },
            { label: "Pagine extra (da \u20AC49,90/pag)", price: "da \u20AC69", note: "a pagina" },
            { label: "Hosting + Assistenza + Modifiche", price: "da \u20AC12", note: "/mese" },
        ],
        cta: "Vedi dettagli",
        link: "/prezzi",
    },
];

const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

export default function ServicesList() {
    const router = useRouter();

    return (
        <section className="py-20 bg-[#0f0f23] border-t border-white/5">
            <div className="container mx-auto px-6 max-w-6xl">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-12"
                >
                    <h2 className="text-2xl font-bold text-white mb-2">I nostri 3 servizi</h2>
                    <p className="text-gray-400">Scegli come vuoi essere online. Ogni servizio funziona anche da solo.</p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6">
                    {serviceCategories.map((cat, idx) => {
                        const Icon = cat.icon;
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden"
                                whileInView="visible"
                                viewport={{ once: true }}
                                variants={fadeUp}
                                transition={{ delay: idx * 0.1 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:border-white/10 transition-all flex flex-col"
                            >
                                <div className="flex items-center gap-3 mb-4">
                                    <div
                                        className="w-10 h-10 rounded-xl flex items-center justify-center"
                                        style={{ backgroundColor: `${cat.color}15` }}
                                    >
                                        <Icon className="w-5 h-5" style={{ color: cat.color }} />
                                    </div>
                                    <div>
                                        <h3 className="text-white font-bold text-sm">{cat.name}</h3>
                                        <p className="text-xs text-gray-500">{cat.subtitle}</p>
                                    </div>
                                </div>

                                <ul className="space-y-3 mb-6 flex-grow">
                                    {cat.items.map((item, i) => (
                                        <li key={i} className="flex justify-between items-start text-sm">
                                            <span className="text-gray-400 text-xs leading-relaxed">{item.label}</span>
                                            <div className="text-right flex-shrink-0 ml-3">
                                                <span className="block text-white font-bold text-xs">{item.price}</span>
                                                {item.note && <span className="text-gray-600 text-[10px]">{item.note}</span>}
                                            </div>
                                        </li>
                                    ))}
                                </ul>

                                <button
                                    onClick={() => router.push(cat.link)}
                                    className="w-full py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                >
                                    {cat.cta} <ArrowRight className="w-3.5 h-3.5" />
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                <div className="text-center mt-8">
                    <p className="text-xs text-gray-600">
                        Tutti i prezzi sono IVA esclusa. Budget pubblicitario separato per i Pack Ads.
                    </p>
                </div>
            </div>
        </section>
    );
}
