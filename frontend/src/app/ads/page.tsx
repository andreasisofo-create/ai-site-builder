"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
    Megaphone, TrendingUp, BarChart3, Search, Target, Zap,
    Check, ChevronDown, Star, ArrowRight, Shield, Brain,
    Rocket, MessageSquare, ImagePlus, Video, Globe,
    Smartphone, DollarSign, Users, Clock, Eye
} from "lucide-react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

// ============ HERO ============
function AdsHero() {
    return (
        <section className="pt-32 pb-20 lg:pt-40 lg:pb-28 relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#22C55E]/20 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.6 }}>
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs uppercase font-bold tracking-widest mb-6">
                        <Megaphone className="w-3.5 h-3.5" />
                        Servizio Ads Management
                    </div>
                    <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                        Ogni euro investito.<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22C55E] to-[#4ADE80]">Diventa un cliente.</span>
                    </h1>
                    <p className="text-gray-400 max-w-2xl mx-auto mb-10 text-lg">
                        Il nostro team gestisce le tue campagne su Google e Meta con il supporto dell&apos;intelligenza artificiale.
                        Tu ricevi i contatti. Noi facciamo tutto il resto.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/#form-contatto"
                            className="px-8 py-4 bg-[#22C55E] hover:bg-[#16A34A] text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-green-900/40 flex items-center justify-center gap-2"
                        >
                            Richiedi consulenza gratuita <ArrowRight className="w-5 h-5" />
                        </Link>
                        <button
                            onClick={() => document.getElementById("come-funziona-ads")?.scrollIntoView({ behavior: "smooth" })}
                            className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-bold text-lg transition-all"
                        >
                            Come funziona
                        </button>
                    </div>
                </motion.div>

                {/* Stats bar */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="max-w-3xl mx-auto mt-16 grid grid-cols-2 lg:grid-cols-4 gap-4"
                >
                    {[
                        { value: "4", label: "Moduli AI dedicati" },
                        { value: "24/7", label: "Ottimizzazione continua" },
                        { value: "-30%", label: "Costo per lead medio" },
                        { value: "7gg", label: "Primi risultati" },
                    ].map((stat, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-[#16162a] border border-white/5 text-center">
                            <div className="text-2xl font-bold text-[#22C55E]">{stat.value}</div>
                            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
                        </div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}

// ============ WHAT WE DO ============
function WhatWeDo() {
    const services = [
        {
            icon: Search,
            title: "Google Ads",
            desc: "Annunci su Ricerca Google, Shopping e Display. Intercettiamo chi cerca i tuoi servizi nella tua zona.",
            features: ["Ricerca keyword", "Annunci RSA", "Google Shopping", "Remarketing"],
        },
        {
            icon: Megaphone,
            title: "Meta Ads",
            desc: "Campagne Instagram e Facebook per raggiungere il tuo pubblico ideale con creativita generate dall'AI.",
            features: ["Instagram Feed & Stories", "Facebook Ads", "Audience personalizzate", "A/B Testing"],
        },
        {
            icon: ImagePlus,
            title: "Contenuti AI",
            desc: "Immagini generate con Gemini AI, video prompt per Seedance 2.0 e copy ottimizzati per ogni piattaforma.",
            features: ["Immagini con Gemini AI", "Video prompt AI", "Copy annunci RSA", "Post social"],
        },
        {
            icon: BarChart3,
            title: "Analytics & Report",
            desc: "Dashboard chiara con tutti i numeri che contano: clic, lead, costo per contatto e ROI.",
            features: ["Report settimanale/mensile", "Costo per lead", "Conversion tracking", "Benchmark settore"],
        },
        {
            icon: Target,
            title: "Landing Page",
            desc: "Pagine di atterraggio ottimizzate per ogni campagna. L'AI analizza e migliora continuamente.",
            features: ["Design ottimizzato", "A/B testing", "Score qualita", "Ottimizzazione CRO"],
        },
        {
            icon: MessageSquare,
            title: "DM Automatici",
            desc: "Rispondi automaticamente ai lead che arrivano da Instagram e Facebook. Nessun contatto perso.",
            features: ["Risposta automatica", "Qualificazione lead", "CRM integrato", "Follow-up AI"],
        },
    ];

    return (
        <section className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Cosa facciamo per te
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        Un ecosistema completo per portarti clienti ogni giorno. Tutto gestito dal nostro team con AI.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {services.map((service, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.08 }}
                            className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:border-[#22C55E]/20 transition-all group"
                        >
                            <div className="w-12 h-12 rounded-xl bg-[#22C55E]/10 flex items-center justify-center mb-4 group-hover:bg-[#22C55E]/20 transition-colors">
                                <service.icon className="w-6 h-6 text-[#22C55E]" />
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2">{service.title}</h3>
                            <p className="text-sm text-gray-400 mb-4 leading-relaxed">{service.desc}</p>
                            <div className="flex flex-wrap gap-2">
                                {service.features.map((feat, i) => (
                                    <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-gray-400 border border-white/5">
                                        {feat}
                                    </span>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ HOW IT WORKS ============
function HowItWorks() {
    const steps = [
        {
            num: "01",
            icon: MessageSquare,
            title: "Consulenza gratuita",
            desc: "Analizziamo la tua attivita, i tuoi obiettivi e il tuo mercato di riferimento. Nessun impegno.",
        },
        {
            num: "02",
            icon: Brain,
            title: "L'AI analizza il mercato",
            desc: "4 moduli AI studiano il tuo settore: keyword, competitor, benchmark e opportunita pubblicitarie.",
        },
        {
            num: "03",
            icon: Rocket,
            title: "Lanciamo le campagne",
            desc: "Creiamo annunci, landing page e contenuti ottimizzati. Le campagne vanno live in 48 ore.",
        },
        {
            num: "04",
            icon: TrendingUp,
            title: "Ottimizziamo ogni settimana",
            desc: "L'AI monitora e ottimizza budget, targeting e creativita. Tu ricevi i lead e il report.",
        },
    ];

    return (
        <section id="come-funziona-ads" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs uppercase font-bold tracking-widest mb-6">
                        <Zap className="w-3 h-3" /> Come funziona
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Dalla consulenza ai clienti<br />in 4 step
                    </h2>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
                    {steps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.12 }}
                            className="relative text-center p-6"
                        >
                            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-[#22C55E]/10 border border-[#22C55E]/20 flex items-center justify-center">
                                <step.icon className="w-6 h-6 text-[#22C55E]" />
                            </div>
                            <div className="text-5xl font-bold text-white/5 mb-2">{step.num}</div>
                            <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                            <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
                            {idx < steps.length - 1 && (
                                <div className="hidden lg:block absolute top-16 -right-3 text-gray-700">
                                    <ArrowRight className="w-6 h-6" />
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ AI PIPELINE ============
function AiPipeline() {
    const modules = [
        {
            icon: Search,
            name: "L'Investigatore",
            subtitle: "Analisi Cliente & Asset",
            desc: "Analizza il sito web del cliente, struttura, contenuti e proposta di valore. Genera un profilo completo del business.",
            outputs: ["Categoria business", "Proposta di valore", "Punteggio landing page", "Catalogo servizi"],
            color: "blue",
        },
        {
            icon: BarChart3,
            name: "L'Analista",
            subtitle: "Trend & Competizione",
            desc: "Studia keyword, competitor, benchmark di settore e trend stagionali. Mappa completa del panorama competitivo.",
            outputs: ["Mappa keyword (volumi, CPC)", "Indice stagionalita", "Stima budget competitivo", "SWOT vs competitor"],
            color: "emerald",
        },
        {
            icon: Brain,
            name: "L'Architetto",
            subtitle: "Piano Marketing",
            desc: "Incrocia i dati dei moduli precedenti per generare campagne, keyword, copy annunci e KPI target.",
            outputs: ["Piano campagne completo", "Copy annunci RSA", "Allocazione budget", "KPI target"],
            color: "violet",
        },
        {
            icon: Rocket,
            name: "Il Broker",
            subtitle: "Gestione & Ottimizzazione",
            desc: "Gestisce il budget come un investitore algoritmico. Ottimizza bid, gestisce A/B test e monitora in tempo reale.",
            outputs: ["Campagne live", "A/B testing automatico", "Bid adjustments real-time", "Alert e report"],
            color: "purple",
        },
    ];

    const colorMap: Record<string, { bg: string; text: string; border: string }> = {
        blue: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/20" },
        emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
        violet: { bg: "bg-violet-500/10", text: "text-violet-400", border: "border-violet-500/20" },
        purple: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/20" },
    };

    return (
        <section className="py-20 lg:py-28 bg-[#0f0f23] relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-[#22C55E]/10 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs uppercase font-bold tracking-widest mb-6">
                        <Brain className="w-3 h-3" /> AI-Powered
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        4 moduli AI lavorano<br />per te, 24/7
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        Dall&apos;analisi del mercato all&apos;ottimizzazione delle campagne: ogni fase e automatizzata
                        con guardrail di sicurezza e supervisione umana.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-6xl mx-auto">
                    {modules.map((module, idx) => {
                        const colors = colorMap[module.color];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                                className={`relative p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:${colors.border} transition-all`}
                            >
                                <div className={`absolute -top-3 left-6 w-7 h-7 rounded-full ${colors.bg} ${colors.border} border flex items-center justify-center text-xs font-bold ${colors.text}`}>
                                    {idx + 1}
                                </div>
                                <div className={`w-12 h-12 rounded-xl ${colors.bg} flex items-center justify-center mt-2 mb-4`}>
                                    <module.icon className={`w-6 h-6 ${colors.text}`} />
                                </div>
                                <h3 className="font-bold text-white text-sm">{module.name}</h3>
                                <p className={`text-xs ${colors.text} font-medium mb-3`}>{module.subtitle}</p>
                                <p className="text-sm text-gray-400 mb-4 leading-relaxed">{module.desc}</p>
                                <div className="space-y-1.5">
                                    {module.outputs.map((output, i) => (
                                        <div key={i} className="flex items-start gap-2">
                                            <div className={`w-1 h-1 rounded-full ${colors.text} mt-1.5 shrink-0`} />
                                            <span className="text-xs text-gray-500">{output}</span>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Safety banner */}
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="mt-12 max-w-3xl mx-auto">
                    <div className="flex items-center gap-4 p-5 rounded-2xl bg-[#16162a] border border-white/5">
                        <Shield className="w-8 h-8 text-emerald-400 flex-shrink-0" />
                        <div>
                            <p className="text-sm font-bold text-white">Guardrail di sicurezza integrati</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Budget cap assoluto, circuit breaker automatico, approvazione umana per decisioni critiche,
                                benchmark validation e anomaly detection. L&apos;AI non puo superare i limiti impostati.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

// ============ CONTENT CREATION ============
function ContentCreation() {
    const tools = [
        {
            icon: ImagePlus,
            title: "Generatore Immagini AI",
            desc: "Crea immagini per i tuoi annunci con Gemini 2.5 Flash. 6 formati disponibili (Feed, Stories, YouTube, Display).",
            badge: "Gemini AI",
        },
        {
            icon: Video,
            title: "Video Creator AI",
            desc: "Genera prompt video ottimizzati per Seedance 2.0. Stili cinematografici, social e product demo.",
            badge: "Seedance 2.0",
        },
        {
            icon: MessageSquare,
            title: "Copy AI per Annunci",
            desc: "15 titoli + 4 descrizioni RSA generati automaticamente. Copy ottimizzato per conversioni.",
            badge: "Multi-Agent AI",
        },
    ];

    return (
        <section className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Creativita generate<br />dall&apos;intelligenza artificiale
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        Non devi pensare a grafiche, testi o video. L&apos;AI crea tutto per te, ottimizzato per ogni piattaforma.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {tools.map((tool, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="p-6 rounded-2xl bg-gradient-to-b from-[#16162a] to-[#12122a] border border-white/5 text-center"
                        >
                            <div className="w-14 h-14 mx-auto rounded-2xl bg-[#22C55E]/10 flex items-center justify-center mb-4">
                                <tool.icon className="w-7 h-7 text-[#22C55E]" />
                            </div>
                            <span className="inline-block text-xs px-3 py-1 rounded-full bg-[#22C55E]/10 text-[#22C55E] font-medium border border-[#22C55E]/20 mb-4">
                                {tool.badge}
                            </span>
                            <h3 className="text-lg font-bold text-white mb-2">{tool.title}</h3>
                            <p className="text-sm text-gray-400 leading-relaxed">{tool.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ PRICING ============
function AdsPricing() {
    const packs = [
        {
            name: "Pack Presenza",
            price: "€499",
            setup: "una tantum",
            subscription: "+ €39/mese",
            desc: "Per chi vuole essere online con un sito professionale.",
            features: [
                "Homepage AI completa",
                "3 pagine extra incluse (4 totali)",
                "Dominio personalizzato (1 anno)",
                "Hosting + SSL + Backup",
                "Modifiche illimitate via chat",
            ],
            highlight: false,
        },
        {
            name: "Pack Clienti",
            price: "€499",
            setup: "una tantum",
            subscription: "+ €199/mese",
            desc: "Per iniziare subito a ricevere clienti da Instagram e Facebook.",
            features: [
                "Tutto del Pack Presenza",
                "Meta Ads (Instagram & Facebook)",
                "Contenuti Base (8 post AI/mese)",
                "Report mensile performance",
                "Supporto via chat",
            ],
            highlight: false,
        },
        {
            name: "Pack Crescita",
            price: "€499",
            setup: "SETUP GRATUITO",
            subscription: "+ €399/mese",
            desc: "Per crescere seriamente con Google e Meta insieme.",
            features: [
                "Sito Web Custom completo (8 pagine)",
                "Dominio personalizzato incluso",
                "Full Ads: Meta Pro + Google Ads",
                "DM automatici ai lead",
                "Contenuti Pro (illimitati)",
                "Report settimanale dettagliato",
                "Manutenzione inclusa",
                "Supporto prioritario",
            ],
            highlight: true,
            tag: "CONSIGLIATO",
        },
        {
            name: "Pack Premium",
            price: "€1.499",
            setup: "SETUP GRATUITO",
            subscription: "+ €999/mese",
            desc: "Per attivita ambiziose. Un'agenzia digitale dedicata.",
            features: [
                "Tutto del Pack Crescita",
                "Pagine sito illimitate",
                "Campagne illimitate su tutti i canali",
                "Account manager dedicato",
                "Strategia marketing mensile",
                "Report personalizzato e call mensile",
                "Supporto 24/7 dedicato",
            ],
            highlight: false,
        },
    ];

    return (
        <section id="prezzi-ads" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Pack completi. Prezzi chiari.
                    </h2>
                    <p className="text-gray-400 text-lg">
                        Soluzioni tutto-incluso con risparmio garantito.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-8">
                    {packs.map((plan, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.4, delay: idx * 0.1 }}
                            className={`relative p-6 rounded-2xl flex flex-col h-full transition-all ${plan.highlight
                                ? "bg-gradient-to-b from-[#22C55E]/15 to-[#16162a] border-2 border-[#22C55E] shadow-[0_0_40px_-10px_rgba(34,197,94,0.3)] scale-[1.02] z-10"
                                : "bg-[#16162a] border border-white/5 hover:border-white/20"
                                }`}
                        >
                            {plan.highlight && plan.tag && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#22C55E] text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                                    {plan.tag}
                                </div>
                            )}
                            <div className="mb-6">
                                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{plan.desc}</p>
                                <div className="flex flex-col">
                                    <div className="flex items-baseline">
                                        <span className="text-3xl font-bold text-white tracking-tight">{plan.price}</span>
                                        <span className="text-gray-500 ml-1 text-sm">{plan.subscription}</span>
                                    </div>
                                    <span className="text-xs text-[#22C55E] font-semibold uppercase tracking-wide mt-1">{plan.setup}</span>
                                </div>
                            </div>
                            <ul className="space-y-3 mb-8 flex-grow">
                                {plan.features.map((feat, i) => (
                                    <li key={i} className="flex items-start gap-2">
                                        <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span className="text-sm text-gray-300">{feat}</span>
                                    </li>
                                ))}
                            </ul>
                            <Link
                                href="/#form-contatto"
                                className={`w-full py-3 rounded-xl font-bold text-sm text-center transition-all block ${plan.highlight
                                    ? "bg-[#22C55E] hover:bg-[#16A34A] text-white shadow-lg"
                                    : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                    }`}
                            >
                                Scegli {plan.name}
                            </Link>
                        </motion.div>
                    ))}
                </div>

                <div className="text-center space-x-4">
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                        * Budget pubblicitario escluso
                    </span>
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                        ** Sconto 15% pagamento annuale
                    </span>
                </div>
            </div>
        </section>
    );
}

// ============ TESTIMONIALS ============
function AdsTestimonials() {
    const reviews = [
        { name: "Marco R.", role: "Ristoratore", text: "Le campagne Meta ci portano 25 coperti in piu a settimana. Il report mensile e chiarissimo, so esattamente quanto mi costa ogni cliente." },
        { name: "Laura M.", role: "Estetista", text: "Prima spendevo in volantini senza sapere se funzionassero. Ora con Google Ads ricevo 15 nuovi contatti al mese e so il costo di ognuno." },
        { name: "Giuseppe V.", role: "Avvocato", text: "Il team gestisce tutto, io ricevo solo i contatti qualificati. In 3 mesi ho recuperato l'investimento e ora il flusso e costante." },
    ];

    return (
        <section className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-white mb-4">Risultati reali, clienti reali</h2>
                </motion.div>
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {reviews.map((rev, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="p-6 rounded-2xl bg-[#16162a] border border-white/5"
                        >
                            <div className="flex gap-0.5 mb-3">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                ))}
                            </div>
                            <p className="text-sm text-gray-300 mb-4 leading-relaxed">&ldquo;{rev.text}&rdquo;</p>
                            <div>
                                <p className="text-white font-bold text-sm">{rev.name}</p>
                                <p className="text-xs text-gray-500">{rev.role}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ FAQ ============
function AdsFaq() {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    const faqs = [
        { q: "Quanto devo spendere di budget pubblicitario?", a: "Il budget pubblicitario e separato dal costo del servizio. Consigliamo un minimo di €300/mese per Meta e €500/mese per Google. Il nostro team ti aiuta a decidere in base ai tuoi obiettivi." },
        { q: "In quanto tempo vedo i risultati?", a: "Le prime richieste arrivano in genere entro 7-14 giorni dall'attivazione delle campagne. I risultati migliorano mese dopo mese grazie all'ottimizzazione continua dell'AI." },
        { q: "Devo creare io i contenuti degli annunci?", a: "No, creiamo noi tutto: testi, immagini, video e grafiche. L'AI genera contenuti ottimizzati per ogni piattaforma e li testa automaticamente." },
        { q: "Come funziona il report?", a: "Ricevi un report dettagliato (settimanale o mensile in base al piano) con clic, impression, lead, costo per contatto e suggerimenti di ottimizzazione. Dashboard sempre accessibile." },
        { q: "Posso scegliere solo il servizio Ads senza il sito?", a: "Si, puoi acquistare i servizi a la carte. Ads Management parte da €149/mese per Meta Ads. Pero un sito ottimizzato migliora drasticamente le conversioni." },
        { q: "Cosa succede se le campagne non performano?", a: "Il sistema ha guardrail automatici: circuit breaker che pausa le campagne se il costo per lead supera la soglia, anomaly detection e revisione settimanale. Non sprechiamo budget." },
        { q: "Posso disdire quando voglio?", a: "Si, nessun vincolo. I piani mensili si possono disdire in qualsiasi momento. I servizi una tantum (sito) restano tuoi." },
        { q: "Gestite anche i miei account social?", a: "I piani con Contenuti AI includono la creazione di post per i social. Il piano Crescita include 8 post AI/mese, il Premium contenuti illimitati. La pubblicazione sui social e gestita dal nostro team." },
    ];

    return (
        <section id="faq-ads" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6 max-w-3xl">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl lg:text-4xl font-bold text-white">Domande frequenti</h2>
                </motion.div>

                <div className="space-y-3">
                    {faqs.map((faq, idx) => (
                        <div
                            key={idx}
                            className="bg-[#16162a] border border-white/5 rounded-xl overflow-hidden transition-all hover:border-white/10"
                        >
                            <button
                                onClick={() => setOpenIndex(idx === openIndex ? null : idx)}
                                className="w-full text-left p-5 flex items-center justify-between"
                            >
                                <span className="font-bold text-white text-sm pr-4">{faq.q}</span>
                                <ChevronDown className={`w-5 h-5 text-[#22C55E] flex-shrink-0 transition-transform ${openIndex === idx ? "rotate-180" : ""}`} />
                            </button>
                            {openIndex === idx && (
                                <div className="px-5 pb-5 text-sm text-gray-400 leading-relaxed">
                                    {faq.a}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ FINAL CTA ============
function FinalCta() {
    return (
        <section className="py-20 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#0a1a0f] to-[#0a0a1a]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#22C55E]/15 via-transparent to-transparent" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Pronto a ricevere<br />clienti ogni giorno?
                    </h2>
                    <p className="text-gray-300 mb-8 text-lg max-w-xl mx-auto">
                        Consulenza gratuita. Analizziamo la tua attivita e ti mostriamo il potenziale delle campagne AI.
                    </p>
                    <Link
                        href="/#form-contatto"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-[#22C55E] hover:bg-[#16A34A] text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-green-900/40"
                    >
                        Richiedi consulenza gratuita <ArrowRight className="w-5 h-5" />
                    </Link>
                </motion.div>
            </div>
        </section>
    );
}

// ============ PAGE ============
export default function AdsPage() {
    return (
        <div className="min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden font-sans">
            <Navbar />
            <main>
                <AdsHero />
                <WhatWeDo />
                <HowItWorks />
                <AiPipeline />
                <ContentCreation />
                <AdsPricing />

                <AdsTestimonials />
                <AdsFaq />
                <FinalCta />
            </main>
            <Footer />
        </div>
    );
}
