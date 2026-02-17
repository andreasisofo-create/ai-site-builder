"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import {
    Sparkles, Zap, MessageSquare, Smartphone, Globe, Search,
    ArrowRight, Megaphone, TrendingUp, BarChart3, ChevronDown,
    Star, Check, Palette, MousePointerClick
} from "lucide-react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

// ============ HERO ============
function AiHero() {
    return (
        <section className="pt-32 pb-20 lg:pt-40 lg:pb-28 relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.6 }}>
                    <h1 className="text-4xl lg:text-6xl font-bold text-white mb-4 leading-tight">
                        Il tuo sito professionale in<br />60 secondi.
                    </h1>
                    <p className="text-xl text-purple-300 font-semibold mb-4">I tuoi clienti, dal giorno dopo.</p>
                    <p className="text-gray-400 max-w-2xl mx-auto mb-10 text-lg">
                        Scegli la tua attività, carica il logo e l&apos;intelligenza artificiale crea il tuo sito.
                        Poi attiviamo campagne pubblicitarie per portarti clienti reali ogni giorno.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
                        <Link
                            href="/auth"
                            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2"
                        >
                            Crea il tuo sito gratis <ArrowRight className="w-5 h-5" />
                        </Link>
                        <button
                            onClick={() => document.getElementById("come-funziona")?.scrollIntoView({ behavior: "smooth" })}
                            className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-bold text-lg transition-all"
                        >
                            Guarda come funziona
                        </button>
                    </div>
                </motion.div>

                {/* Browser Mockup */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.3 }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="bg-[#1a1a2e] border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-purple-500/10">
                        <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#12122a]">
                            <div className="flex gap-1.5">
                                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                                <div className="w-3 h-3 rounded-full bg-green-500/60" />
                            </div>
                            <div className="flex-1 text-center">
                                <div className="inline-flex items-center gap-2 px-4 py-1 bg-white/5 rounded-full text-xs text-gray-400">
                                    <Globe className="w-3 h-3" /> iltuosito.e-quipe.app
                                </div>
                            </div>
                        </div>
                        <div className="aspect-video bg-gradient-to-br from-[#16162a] to-[#0f0f1a] flex items-center justify-center relative">
                            <div className="text-center space-y-4">
                                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                                    <Sparkles className="w-8 h-8 text-purple-400" />
                                </div>
                                <p className="text-gray-500 text-sm">La tua AI sta creando il sito...</p>
                                <div className="w-48 h-1.5 mx-auto bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full w-2/3 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" />
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

// ============ 3 STEPS ============
function Steps() {
    const steps = [
        { num: "01", icon: MessageSquare, title: "Descrivi la tua attività", desc: "Rispondi a 3 semplici domande. Nome, tipo di attività, i tuoi servizi principali. Non serve altro." },
        { num: "02", icon: Sparkles, title: "L'AI genera il tuo sito", desc: "In 60 secondi hai un sito completo. Testi, immagini, colori e animazioni. Tutto ottimizzato." },
        { num: "03", icon: Globe, title: "Pubblica e trova clienti", desc: "Il sito va online subito. Attiva le campagne pubblicitarie per portarti contatti reali ogni giorno." },
    ];

    return (
        <section id="come-funziona" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest mb-6">
                        <Zap className="w-3 h-3" /> 3 Passaggi
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Da zero al tuo sito, in meno di<br />un caffè.
                    </h2>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    {steps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.15 }}
                            className="text-center"
                        >
                            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                                <step.icon className="w-6 h-6 text-purple-400" />
                            </div>
                            <div className="text-5xl font-bold text-white/5 mb-2">{step.num}</div>
                            <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                            <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ FEATURES ============
function Features() {
    const [tab, setTab] = useState<"siti" | "ads">("siti");

    const siteFeatures = [
        { icon: Zap, title: "Sito pronto in 60 secondi", desc: "Rispondi a 3 domande. Testi, foto, colori: tutto generato dall'AI." },
        { icon: Palette, title: "7+ stili professionali", desc: "L'AI sceglie design portfolio per la tua attività. Oppure scegli tu." },
        { icon: MessageSquare, title: "Modifiche con la chat", desc: "Dì all'AI cosa cambiare. \"Cambia il colore\", \"aggiungi un testo\". Fatto." },
        { icon: Smartphone, title: "Perfetto su qualsiasi dispositivo", desc: "Il sito si adatta automaticamente a smartphone, tablet e desktop." },
        { icon: MousePointerClick, title: "Online con un click", desc: "Hosting, certificato SSL e dominio: è tutto incluso. Pubblica subito." },
        { icon: Search, title: "Pensato per Google", desc: "L'AI ottimizza titoli, descrizioni per i motori di ricerca automaticamente." },
    ];

    const adsFeatures = [
        { icon: Megaphone, title: "Meta Ads incluse", desc: "Campagne Instagram e Facebook gestite dal nostro team con AI." },
        { icon: TrendingUp, title: "Google Ads ottimizzate", desc: "Annunci su Google per chi cerca i tuoi servizi nella tua zona." },
        { icon: BarChart3, title: "Report mensile", desc: "Dashboard chiara con clic, lead e costo per contatto." },
        { icon: MessageSquare, title: "Contenuti AI", desc: "Post social, testi annunci e grafiche generate dall'intelligenza artificiale." },
        { icon: Globe, title: "Landing page dedicate", desc: "Pagine ottimizzate per ogni campagna pubblicitaria." },
        { icon: Zap, title: "DM automatici", desc: "Rispondi automaticamente ai lead che arrivano da Instagram e Facebook." },
    ];

    const features = tab === "siti" ? siteFeatures : adsFeatures;

    return (
        <section id="funzionalita" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-8">
                        Tutto quello che ti serve per<br />essere online
                    </h2>
                    {/* Toggle */}
                    <div className="inline-flex bg-white/5 rounded-full p-1 border border-white/10">
                        <button
                            onClick={() => setTab("siti")}
                            className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${tab === "siti" ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md" : "text-gray-400 hover:text-white"}`}
                        >
                            Crea Siti
                        </button>
                        <button
                            onClick={() => setTab("ads")}
                            className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${tab === "ads" ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md" : "text-gray-400 hover:text-white"}`}
                        >
                            Trova Clienti
                        </button>
                    </div>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {features.map((feat, idx) => (
                        <motion.div
                            key={`${tab}-${idx}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.4, delay: idx * 0.08 }}
                            className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:border-purple-500/20 transition-all"
                        >
                            <feat.icon className="w-6 h-6 text-purple-400 mb-3" />
                            <h3 className="font-bold text-white mb-1">{feat.title}</h3>
                            <p className="text-sm text-gray-400">{feat.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ ADS SECTION ============
function AdsSection() {
    const cards = [
        { icon: Megaphone, title: "Meta Ads", items: ["Instagram + Facebook Ads", "Audience personalizzate", "A/B testing automatico", "Creatività generate con AI"] },
        { icon: Search, title: "Google Ads", items: ["Annunci su Ricerca Google", "Keyword della tua zona", "Budget ottimizzato con AI", "Monitoraggio conversioni intelligente"] },
        { icon: BarChart3, title: "Report Mensile", items: ["Dashboard risultati", "Clic, lead e conversioni", "Costo per contatto", "Suggerimenti di auto-ottimizzazione"] },
    ];

    return (
        <section id="servizio-ads" className="py-20 lg:py-28 bg-[#0f0f23] relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest mb-6">
                        <TrendingUp className="w-3 h-3" /> Servizio Ads Management
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Non basta avere un sito.<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Servono clienti.</span>
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        Il nostro team gestisce le tue campagne Meta e Google Ads con il supporto dell&apos;intelligenza artificiale.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
                    {cards.map((card, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="p-6 rounded-2xl bg-[#16162a] border border-white/5"
                        >
                            <card.icon className="w-8 h-8 text-purple-400 mb-4" />
                            <h3 className="text-lg font-bold text-white mb-4">{card.title}</h3>
                            <ul className="space-y-2">
                                {card.items.map((item, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-gray-400">
                                        <Check className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </motion.div>
                    ))}
                </div>

                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center">
                    <div className="inline-block p-6 rounded-2xl bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/20">
                        <p className="text-sm text-gray-300 mb-1"><strong>Come funziona il servizio Ads</strong></p>
                        <p className="text-xs text-gray-500">
                            Analizziamo la tua attività → Creiamo le campagne → Ottimizziamo ogni settimana → Ti mandiamo il report
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

// ============ PORTFOLIO ============
function AiPortfolio() {
    const sites = [
        { name: "RestInOne", image: "/images/demos/restinone.png" },
        { name: "Professional Force", image: "/images/demos/professionalforce.png" },
        { name: "Fondazione Italiana Sport", image: "/images/demos/fondazione.png" },
        { name: "Now Now", image: "/images/demos/nownow.png" },
        { name: "Rally Roma Capitale", image: "/images/demos/rallyroma.png" },
        { name: "Max Rendina", image: "/images/demos/maxrendina.png" },
    ];

    return (
        <section className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Loro l&apos;hanno già fatto</h2>
                    <p className="text-gray-400">Attività reali che sono andate online con E-quipe.</p>
                </motion.div>

                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6 max-w-5xl mx-auto">
                    {sites.map((site, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.08 }}
                            className="group rounded-2xl overflow-hidden border border-white/5 hover:border-purple-500/30 transition-all bg-[#16162a]"
                        >
                            <div className="relative aspect-[4/3] overflow-hidden">
                                <Image
                                    src={site.image}
                                    alt={site.name}
                                    fill
                                    className="object-cover object-top transition-transform duration-500 group-hover:scale-105"
                                    sizes="(max-width: 768px) 50vw, 33vw"
                                />
                            </div>
                            <div className="p-3 text-center">
                                <p className="text-sm font-medium text-white">{site.name}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

// ============ TESTIMONIALS ============
function Testimonials() {
    const reviews = [
        { name: "Marco R.", role: "Ristoratore", text: "Ho creato il sito in pausa pranzo. Il mio vecchio webmaster ci ha messo 3 mesi. Incredibile davvero." },
        { name: "Laura M.", role: "Estetista", text: "Non ci capisco nulla di tecnologia. Ma in 60 secondi avevo il sito online. E le campagne Google mi portano 15 clienti nuovi al mese." },
        { name: "Giuseppe V.", role: "Avvocato", text: "Le campagne Google ci portano 15 contatti al mese. Con il report mensile so esattamente quanto mi costa ogni nuovo cliente." },
    ];

    return (
        <section className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
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

// ============ PRICING ============
function AiPricing() {
    const adsPlans = [
        {
            name: "Business",
            price: "€49",
            period: "/mese",
            desc: "Per chi vuole un sito completo e autonomo.",
            features: ["Sito AI multi-pagina (5 pag)", "Dominio personalizzato", "Hosting + SSL + Backup", "Supporto prioritario"],
            cta: "Scegli Business",
            highlight: false,
        },
        {
            name: "Crescita",
            price: "€99",
            period: "/mese",
            desc: "Sito + campagne per portarti clienti.",
            features: ["Tutto di Business", "Meta Ads (Instagram + Facebook)", "Contenuti AI (4 post/mese)", "Report mensile performance", "Landing page dedicate"],
            cta: "Scegli Crescita",
            highlight: true,
            tag: "CONSIGLIATO",
        },
        {
            name: "Premium",
            price: "€199",
            period: "/mese",
            desc: "Sito + Full Ads + contenuti Pro.",
            features: ["Tutto di Crescita", "Google Ads incluso", "1 video + 1 foto a settimana", "Report settimanale"],
            cta: "Scegli Premium",
            highlight: false,
        },
    ];

    return (
        <section id="prezzi-ai" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Prezzi chiari. Nessuna<br />sorpresa.
                    </h2>
                    <p className="text-gray-400 text-lg">
                        Parti col sito, aggiungi le campagne quando vuoi crescere.
                    </p>
                </motion.div>

                {/* SITO BASE - standalone blue card */}
                <motion.div
                    initial="hidden" whileInView="visible" viewport={{ once: true }}
                    variants={fadeUp} transition={{ duration: 0.5 }}
                    className="max-w-2xl mx-auto mb-12"
                >
                    <div className="text-center mb-4">
                        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#0090FF]/10 border border-[#0090FF]/30 text-[#0090FF] text-xs uppercase font-bold tracking-widest">
                            <Globe className="w-3.5 h-3.5" /> Solo Sito Web
                        </span>
                    </div>
                    <div className="relative p-8 rounded-2xl bg-gradient-to-br from-[#0090FF]/20 via-[#0060CC]/10 to-[#16162a] border-2 border-[#0090FF]/40 shadow-[0_0_50px_-15px_rgba(0,144,255,0.3)]">
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                            <div className="flex-1">
                                <h3 className="text-2xl font-bold text-white mb-2">Sito Base</h3>
                                <p className="text-gray-300 mb-4">Il tuo sito AI, pronto per andare online. Paghi una volta, nessun abbonamento.</p>
                                <ul className="grid grid-cols-2 gap-2">
                                    {["Sito AI completo (5 pagine)", "Dominio e-quipe.app", "Hosting + SSL incluso", "Modifiche via chat (5/mese)"].map((feat, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <Check className="w-4 h-4 text-[#0090FF] mt-0.5 flex-shrink-0" />
                                            <span className="text-sm text-gray-300">{feat}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="text-center md:text-right flex flex-col items-center md:items-end gap-3 md:min-w-[180px]">
                                <div>
                                    <span className="text-4xl font-bold text-white">€199</span>
                                    <span className="text-gray-400 ml-1 text-sm">una tantum</span>
                                </div>
                                <span className="text-xs text-[#0090FF] font-semibold">Nessun costo mensile</span>
                                <Link
                                    href="/auth"
                                    className="px-8 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-blue-900/30 block"
                                >
                                    Crea il tuo sito
                                </Link>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Divider */}
                <div className="max-w-4xl mx-auto mb-12 flex items-center gap-4">
                    <div className="flex-1 h-px bg-white/10" />
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest">
                        <TrendingUp className="w-3.5 h-3.5" /> Sito + Ads — Porta clienti ogni mese
                    </span>
                    <div className="flex-1 h-px bg-white/10" />
                </div>

                {/* ADS PLANS - 3 cards */}
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-8">
                    {adsPlans.map((plan, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden" whileInView="visible" viewport={{ once: true }}
                            variants={fadeUp} transition={{ duration: 0.4, delay: idx * 0.1 }}
                            className={`relative p-6 rounded-2xl flex flex-col h-full transition-all ${plan.highlight
                                    ? "bg-gradient-to-b from-purple-900/40 to-[#16162a] border-2 border-purple-500 shadow-[0_0_40px_-10px_rgba(147,51,234,0.3)] scale-[1.02] z-10"
                                    : "bg-[#16162a] border border-white/5 hover:border-white/20"
                                }`}
                        >
                            {plan.highlight && plan.tag && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                                    {plan.tag}
                                </div>
                            )}
                            <div className="mb-6">
                                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{plan.desc}</p>
                                <div className="flex items-baseline">
                                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                                    <span className="text-gray-500 ml-1 text-sm">{plan.period}</span>
                                </div>
                            </div>
                            <ul className="space-y-3 mb-8 flex-grow">
                                {plan.features.map((feat, i) => (
                                    <li key={i} className="flex items-start gap-2">
                                        <Check className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                                        <span className="text-sm text-gray-300">{feat}</span>
                                    </li>
                                ))}
                            </ul>
                            <Link
                                href="/auth"
                                className={`w-full py-3 rounded-xl font-bold text-sm text-center transition-all block ${plan.highlight
                                        ? "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg"
                                        : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                    }`}
                            >
                                {plan.cta}
                            </Link>
                        </motion.div>
                    ))}
                </div>

                <div className="text-center text-sm text-gray-500">
                    * Budget pubblicitario escluso dai piani Crescita e Premium
                </div>
            </div>
        </section>
    );
}

// ============ FAQ ============
function AiFaq() {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    const faqs = [
        { q: "Devo saper programmare?", a: "Assolutamente no. Rispondi a 3 domande e l'AI crea tutto: testi, immagini, colori, animazioni. Puoi modificare qualsiasi cosa con la chat, senza toccare codice." },
        { q: "Quanto ci metto a creare il sito?", a: "60 secondi. Letteralmente. Rispondi alle domande, l'AI genera il sito completo. Poi puoi modificarlo quanto vuoi." },
        { q: "Posso usare il mio dominio (es. mionome.it)?", a: "Sì, dal piano Business in su puoi collegare il tuo dominio personalizzato. Con il piano base usi un sottodominio gratuito e-quipe.app." },
        { q: "Come funzionano le campagne pubblicitarie?", a: "Il nostro team crea e gestisce le campagne su Meta (Instagram + Facebook) e Google. L'AI ottimizza budget e targeting. Tu ricevi i contatti." },
        { q: "Quanto devo spendere di pubblicità?", a: "Il budget pubblicitario è separato dal costo del piano. Consigliamo un minimo di €300/mese per Meta e €500/mese per Google. Il nostro team ti aiuta a decidere." },
        { q: "Posso iniziare con il sito e aggiungere le campagne dopo?", a: "Certo! Puoi partire col piano Sito Base o Business e passare a Crescita o Premium quando vuoi. L'upgrade è immediato." },
        { q: "In quanto tempo vedo i risultati delle campagne?", a: "Le prime richieste arrivano in genere entro 7-14 giorni dall'attivazione. I risultati migliorano mese dopo mese grazie all'ottimizzazione continua dell'AI." },
        { q: "Posso disdire quando voglio?", a: "Sì, nessun vincolo. Puoi disdire il piano mensile in qualsiasi momento. Il sito base una tantum resta tuo." },
    ];

    return (
        <section id="faq-ai" className="py-20 lg:py-28 bg-[#0f0f23]">
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
                                <ChevronDown className={`w-5 h-5 text-purple-400 flex-shrink-0 transition-transform ${openIndex === idx ? "rotate-180" : ""}`} />
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
            <div className="absolute inset-0 bg-gradient-to-r from-purple-900/60 to-blue-900/60" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-600/20 via-transparent to-transparent" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Pronto a portare la tua attività<br />online?
                    </h2>
                    <p className="text-gray-300 mb-8 text-lg">
                        Crea il tuo sito in 60 secondi. Gratis, senza carta di credito.
                    </p>
                    <Link
                        href="/auth"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-white text-[#0a0a1a] rounded-xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg"
                    >
                        Crea il tuo sito gratis <Sparkles className="w-5 h-5 text-purple-600" />
                    </Link>
                </motion.div>
            </div>
        </section>
    );
}

// ============ PAGE ============
export default function AiBuilderPage() {
    return (
        <div className="min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden font-sans">
            <Navbar variant="ai" />
            <main>
                <AiHero />
                <Steps />
                <Features />
                <AdsSection />
                <AiPortfolio />
                <Testimonials />
                <AiPricing />
                <AiFaq />
                <FinalCta />
            </main>
            <Footer />
        </div>
    );
}
