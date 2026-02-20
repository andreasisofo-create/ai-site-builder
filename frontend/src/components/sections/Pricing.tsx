"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Check, Sparkles, Building2, ArrowRight } from "lucide-react";

// ============ AI BUILDER PLANS ============
const aiBuilderPlans = [
    {
        name: "Prova Gratuita",
        slug: "ai-builder-free",
        price: "Gratis",
        period: "",
        description: "Crea il tuo sito con l\u2019AI senza pagare nulla. Vedi il risultato e decidi.",
        features: [
            "Generazione sito AI completa",
            "Anteprima desktop e mobile",
            "5 modifiche di prova via chat",
            "3 stili professionali",
        ],
        limitations: [
            "Solo anteprima privata, non va online",
            "Nessun dominio o hosting",
        ],
        highlight: false,
        isFree: true,
    },
    {
        name: "Starter",
        slug: "ai-builder-starter",
        price: "\u20AC19,90",
        period: "/mese",
        description: "Il tuo sito AI online, con tutto l\u2019essenziale.",
        features: [
            "Fino a 5 pagine generate dall\u2019AI",
            "Sottodominio: tuosito.e-quipe.app",
            "Hosting veloce + SSL incluso",
            "Mobile responsive",
            "50 modifiche AI al mese",
            "SEO base: titoli e meta description AI",
            "Supporto email (48h)",
        ],
        highlight: false,
    },
    {
        name: "Pro",
        slug: "ai-builder-pro",
        price: "\u20AC39",
        period: "/mese",
        description: "Sito completo con dominio personalizzato e SEO avanzato.",
        features: [
            "Fino a 15 pagine generate dall\u2019AI",
            "Dominio personalizzato (.it/.com) incluso",
            "Hosting veloce + SSL + Backup giornaliero",
            "200 modifiche AI al mese",
            "7+ stili professionali",
            "SEO avanzato + Schema + Sitemap XML",
            "Google Search Console setup guidato",
            "Dashboard traffico + Report mensile",
            "Supporto chat prioritario (12h)",
            "Onboarding assistito",
        ],
        highlight: true,
        tag: "CONSIGLIATO",
    },
];

// ============ SITO AGENZIA PLANS ============
const sitoAgenziaCreation = {
    homepage: { price: "\u20AC349", note: "una tantum" },
    paginaExtra: { price: "\u20AC69", note: "a pagina" },
    packs: [
        { pages: 3, price: "\u20AC189", perPage: "\u20AC63/pag", saving: "-9%" },
        { pages: 5, price: "\u20AC299", perPage: "\u20AC59,80/pag", saving: "-13%" },
        { pages: 10, price: "\u20AC499", perPage: "\u20AC49,90/pag", saving: "-28%" },
    ],
};

const sitoAgenziaMonthly = [
    {
        name: "Hosting",
        slug: "sito-agenzia-hosting",
        price: "\u20AC12",
        period: "/mese",
        description: "Il minimo per tenere il sito online.",
        features: [
            "Hosting veloce server europei",
            "SSL (https) incluso",
            "Dominio incluso (1\u00B0 anno)",
            "Backup settimanale",
            "Aggiornamenti sicurezza server",
        ],
        highlight: false,
    },
    {
        name: "Hosting + Assistenza",
        slug: "sito-agenzia-assistenza",
        price: "\u20AC35",
        period: "/mese",
        description: "Il sito monitorato e aggiornato. Dormi tranquillo.",
        features: [
            "Tutto di Hosting, pi\u00F9:",
            "Assistenza tecnica email (24h)",
            "Monitoraggio uptime attivo",
            "Backup giornaliero",
            "Aggiornamenti sicurezza proattivi",
            "Ottimizzazione performance periodica",
            "Report trimestrale",
        ],
        highlight: false,
    },
    {
        name: "Hosting + Assistenza + Modifiche",
        slug: "sito-agenzia-completo",
        price: "\u20AC79",
        period: "/mese",
        description: "Servizio completo. Scrivi in chat cosa vuoi cambiare e lo facciamo noi.",
        features: [
            "Tutto di Hosting + Assistenza, pi\u00F9:",
            "Modifiche contenuti illimitate via chat",
            "Aggiunta nuove sezioni",
            "Aggiornamento men\u00F9, listini, orari, promo",
            "Gallery fotografiche",
            "Piccoli interventi grafici",
            "SEO continuo",
            "Report mensile traffico",
            "Supporto chat prioritario (12h)",
        ],
        highlight: true,
        tag: "PI\u00D9 SCELTO",
    },
];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Pricing() {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<"ai-builder" | "sito-agenzia">("ai-builder");

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
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Prezzi chiari. Nessuna sorpresa.</h2>
                    <p className="text-xl text-gray-400 mb-8">
                        Due strade per il tuo sito web. Scegli quella che fa per te.
                    </p>

                    {/* Tab switcher */}
                    <div className="inline-flex bg-[#16162a] rounded-xl p-1 border border-white/5">
                        <button
                            onClick={() => setActiveTab("ai-builder")}
                            className={`flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-bold transition-all ${
                                activeTab === "ai-builder"
                                    ? "bg-[#0090FF] text-white shadow-lg"
                                    : "text-gray-400 hover:text-white"
                            }`}
                        >
                            <Sparkles className="w-4 h-4" />
                            AI Builder (Self-service)
                        </button>
                        <button
                            onClick={() => setActiveTab("sito-agenzia")}
                            className={`flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-bold transition-all ${
                                activeTab === "sito-agenzia"
                                    ? "bg-[#0090FF] text-white shadow-lg"
                                    : "text-gray-400 hover:text-white"
                            }`}
                        >
                            <Building2 className="w-4 h-4" />
                            Sito Su Misura (Agenzia)
                        </button>
                    </div>
                </motion.div>

                {/* AI BUILDER TAB */}
                {activeTab === "ai-builder" && (
                    <>
                        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-8">
                            {aiBuilderPlans.map((plan, idx) => (
                                <motion.div
                                    key={idx}
                                    initial="hidden"
                                    whileInView="visible"
                                    viewport={{ once: true, margin: "-50px" }}
                                    variants={fadeUp}
                                    transition={{ duration: 0.4, delay: idx * 0.1 }}
                                    className={`relative p-6 rounded-2xl flex flex-col h-full bg-[#16162a] border transition-all ${
                                        plan.highlight
                                            ? "border-[#0090FF] shadow-[0_0_30px_-10px_rgba(0,144,255,0.3)] scale-[1.02] z-10"
                                            : "border-white/5 hover:border-white/20"
                                    }`}
                                >
                                    {plan.highlight && plan.tag && (
                                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#0090FF] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                            {plan.tag}
                                        </div>
                                    )}

                                    <div className="mb-6">
                                        <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                        <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{plan.description}</p>
                                        <div className="flex items-baseline">
                                            <span className={`text-3xl font-bold tracking-tight ${plan.isFree ? "text-green-400" : "text-white"}`}>
                                                {plan.price}
                                            </span>
                                            {plan.period && <span className="text-gray-500 ml-1 text-sm">{plan.period}</span>}
                                        </div>
                                    </div>

                                    <ul className="space-y-3 mb-4 flex-grow">
                                        {plan.features.map((feat, i) => (
                                            <li key={i} className="flex items-start gap-3">
                                                <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                <span className="text-sm text-gray-300">{feat}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    {"limitations" in plan && plan.limitations && (
                                        <ul className="space-y-2 mb-6 pt-3 border-t border-white/5">
                                            {plan.limitations.map((lim, i) => (
                                                <li key={i} className="flex items-start gap-3">
                                                    <span className="text-gray-600 mt-0.5 flex-shrink-0 text-xs">&mdash;</span>
                                                    <span className="text-xs text-gray-500">{lim}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    )}

                                    <button
                                        onClick={() => plan.isFree ? router.push("/dashboard") : handleCheckout(plan.slug)}
                                        className={`w-full py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                                            plan.highlight
                                                ? "bg-[#0090FF] hover:bg-[#0070C9] text-white shadow-lg"
                                                : plan.isFree
                                                    ? "bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20"
                                                    : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                        }`}
                                    >
                                        {plan.isFree ? "Prova Gratis" : `Scegli ${plan.name}`}
                                    </button>
                                </motion.div>
                            ))}
                        </div>

                        {/* Cross-sell with Ads */}
                        <motion.div
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                            className="max-w-3xl mx-auto mb-8"
                        >
                            <div className="flex flex-col sm:flex-row items-center gap-4 p-5 rounded-2xl bg-[#16162a] border border-[#22C55E]/20">
                                <div className="flex-grow">
                                    <p className="text-sm font-bold text-white">Aggiungi un Pack Ads e risparmi il 15%</p>
                                    <p className="text-xs text-gray-400 mt-1">
                                        Starter a <span className="text-green-400 font-bold">&euro;16,90/mese</span> &middot; Pro a <span className="text-green-400 font-bold">&euro;33/mese</span> con qualsiasi pack Ads attivo.
                                    </p>
                                </div>
                                <button
                                    onClick={() => router.push("/ads#prezzi-ads")}
                                    className="flex items-center gap-1 px-4 py-2 rounded-lg bg-[#22C55E]/10 text-[#22C55E] text-sm font-bold border border-[#22C55E]/20 hover:bg-[#22C55E]/20 transition-all whitespace-nowrap"
                                >
                                    Vedi Pack Ads <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    </>
                )}

                {/* SITO AGENZIA TAB */}
                {activeTab === "sito-agenzia" && (
                    <>
                        {/* Creation pricing */}
                        <motion.div
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                            className="max-w-4xl mx-auto mb-12"
                        >
                            <h3 className="text-xl font-bold text-white mb-6 text-center">Creazione del sito (una tantum)</h3>
                            <div className="grid md:grid-cols-2 gap-6 mb-6">
                                <div className="p-6 rounded-2xl bg-[#16162a] border border-white/5">
                                    <h4 className="text-white font-bold mb-1">Homepage</h4>
                                    <p className="text-xs text-gray-400 mb-3">Design personalizzato, hero, sezioni principali, testi AI, SEO, form contatto, Google Maps</p>
                                    <div className="flex items-baseline">
                                        <span className="text-2xl font-bold text-white">{sitoAgenziaCreation.homepage.price}</span>
                                        <span className="text-gray-500 ml-2 text-sm">{sitoAgenziaCreation.homepage.note}</span>
                                    </div>
                                </div>
                                <div className="p-6 rounded-2xl bg-[#16162a] border border-white/5">
                                    <h4 className="text-white font-bold mb-1">Pagina Extra</h4>
                                    <p className="text-xs text-gray-400 mb-3">Servizi, chi siamo, gallery, FAQ, blog, listino, prenotazioni</p>
                                    <div className="flex items-baseline">
                                        <span className="text-2xl font-bold text-white">{sitoAgenziaCreation.paginaExtra.price}</span>
                                        <span className="text-gray-500 ml-2 text-sm">{sitoAgenziaCreation.paginaExtra.note}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                                {sitoAgenziaCreation.packs.map((pack, idx) => (
                                    <div key={idx} className="p-4 rounded-xl bg-[#16162a] border border-white/5 text-center">
                                        <div className="text-xs text-[#0090FF] font-bold uppercase mb-1">Pack {pack.pages} pagine</div>
                                        <div className="text-lg font-bold text-white">{pack.price}</div>
                                        <div className="text-xs text-gray-500">{pack.perPage}</div>
                                        <div className="text-xs text-green-400 font-semibold mt-1">{pack.saving}</div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Monthly plans */}
                        <h3 className="text-xl font-bold text-white mb-6 text-center">Canoni mensili post-consegna</h3>
                        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-8">
                            {sitoAgenziaMonthly.map((plan, idx) => (
                                <motion.div
                                    key={idx}
                                    initial="hidden"
                                    whileInView="visible"
                                    viewport={{ once: true, margin: "-50px" }}
                                    variants={fadeUp}
                                    transition={{ duration: 0.4, delay: idx * 0.1 }}
                                    className={`relative p-6 rounded-2xl flex flex-col h-full bg-[#16162a] border transition-all ${
                                        plan.highlight
                                            ? "border-[#0090FF] shadow-[0_0_30px_-10px_rgba(0,144,255,0.3)] scale-[1.02] z-10"
                                            : "border-white/5 hover:border-white/20"
                                    }`}
                                >
                                    {"tag" in plan && plan.tag && (
                                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#0090FF] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                            {plan.tag}
                                        </div>
                                    )}

                                    <div className="mb-6">
                                        <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                        <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{plan.description}</p>
                                        <div className="flex items-baseline">
                                            <span className="text-3xl font-bold text-white tracking-tight">{plan.price}</span>
                                            <span className="text-gray-500 ml-1 text-sm">{plan.period}</span>
                                        </div>
                                    </div>

                                    <ul className="space-y-3 mb-8 flex-grow">
                                        {plan.features.map((feat, i) => (
                                            <li key={i} className="flex items-start gap-3">
                                                <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                <span className="text-sm text-gray-300">{feat}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    <button
                                        onClick={() => handleCheckout(plan.slug)}
                                        className={`w-full py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                                            plan.highlight
                                                ? "bg-[#0090FF] hover:bg-[#0070C9] text-white shadow-lg"
                                                : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                        }`}
                                    >
                                        {`Scegli ${plan.name.split(" + ").pop()}`}
                                    </button>
                                </motion.div>
                            ))}
                        </div>

                        {/* Servizi extra */}
                        <motion.div
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                            className="max-w-3xl mx-auto"
                        >
                            <div className="p-5 rounded-2xl bg-[#16162a] border border-white/5">
                                <h4 className="text-sm font-bold text-white mb-3">Servizi extra a consumo</h4>
                                <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-xs">
                                    <div className="flex justify-between text-gray-400"><span>Integrazione prenotazioni</span><span className="text-white font-bold">da &euro;199</span></div>
                                    <div className="flex justify-between text-gray-400"><span>E-commerce base (20 prodotti)</span><span className="text-white font-bold">da &euro;499</span></div>
                                    <div className="flex justify-between text-gray-400"><span>WhatsApp Business</span><span className="text-white font-bold">&euro;99</span></div>
                                    <div className="flex justify-between text-gray-400"><span>Google Business Profile</span><span className="text-white font-bold">&euro;79</span></div>
                                    <div className="flex justify-between text-gray-400"><span>Shooting fotografico</span><span className="text-white font-bold">da &euro;299</span></div>
                                    <div className="flex justify-between text-gray-400"><span>Multilingua</span><span className="text-white font-bold">da &euro;199/lingua</span></div>
                                </div>
                            </div>
                        </motion.div>
                    </>
                )}

                {/* Notes */}
                <div className="text-center mt-8">
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5 mx-2">
                        Prezzi IVA esclusa
                    </span>
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5 mx-2">
                        Sconto 15% pagamento annuale
                    </span>
                </div>
            </div>
        </section>
    );
}
