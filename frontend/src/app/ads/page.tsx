"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Megaphone, TrendingUp, BarChart3, Search, Target, Zap,
    Check, ChevronDown, Star, ArrowRight, Shield, Brain,
    Rocket, MessageSquare, ImagePlus, Video, Globe,
    Smartphone, DollarSign, Users, Clock, Eye
} from "lucide-react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";
import { useLanguage, translations } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";

// Ads pricing data — matches pack-ads-equipe.md
const ADS_CHANNELS = {
    meta: {
        label: "Meta Ads",
        subtitle: "Instagram & Facebook",
        plans: [
            {
                name: "META BASE",
                slug: "meta-ads-base",
                fee: "\u20AC199",
                percent: "15%",
                setup: "\u20AC299 setup",
                desc: "Controllo 2x/settimana, report mensile, supporto email 48h.",
                features: [
                    "Campagne illimitate Instagram & Facebook",
                    "Contenuti AI illimitati (post, grafiche, video)",
                    "A/B testing automatico",
                    "DM automatici ai lead",
                    "Tracking Pixel + Conversions API",
                    "Ottimizzazione settimanale",
                    "Report mensile",
                ],
                budget: "da \u20AC300 a \u20AC800/mese",
                example: "Budget \u20AC500 \u2192 \u20AC199 + \u20AC75 = \u20AC274/mese",
            },
            {
                name: "META PRO",
                slug: "meta-ads-pro",
                fee: "\u20AC349",
                percent: "12%",
                setup: "\u20AC199 setup",
                desc: "Controllo giornaliero, review creativit\u00E0, dashboard live.",
                features: [
                    "Tutto di META BASE",
                    "Controllo giornaliero campagne",
                    "Ottimizzazione 3x/settimana",
                    "Review umana ogni creativit\u00E0",
                    "Dashboard live in tempo reale",
                    "Report quindicinale",
                    "Supporto chat prioritario 24h",
                    "Consulenza strategica trimestrale",
                ],
                budget: "da \u20AC800 a \u20AC2.500/mese",
                example: "Budget \u20AC1.200 \u2192 \u20AC349 + \u20AC144 = \u20AC493/mese",
                highlight: true,
            },
            {
                name: "META ELITE",
                slug: "meta-ads-elite",
                fee: "\u20AC549",
                percent: "10%",
                setup: "Setup incluso (min. 6 mesi)",
                desc: "Alert real-time, ottimizzazione quotidiana, call mensile.",
                features: [
                    "Tutto di META PRO",
                    "Alert real-time + intervento immediato",
                    "Ottimizzazione quotidiana",
                    "Supervisione completa creativit\u00E0",
                    "Report settimanale + Dashboard live",
                    "Supporto dedicato entro 4h",
                    "Consulenza strategica mensile con call",
                ],
                budget: "da \u20AC2.500/mese in su",
                example: "Budget \u20AC3.000 \u2192 \u20AC549 + \u20AC300 = \u20AC849/mese",
            },
        ],
    },
    google: {
        label: "Google Ads",
        subtitle: "Ricerca, Display & Maps",
        plans: [
            {
                name: "GOOGLE BASE",
                slug: "google-ads-base",
                fee: "\u20AC249",
                percent: "15%",
                setup: "\u20AC299 setup",
                desc: "Campagne Ricerca, Display, Maps, Shopping. Report mensile.",
                features: [
                    "Campagne illimitate (Ricerca, Display, Maps, Shopping)",
                    "Keyword research + negative keywords AI",
                    "Annunci RSA + tutte le estensioni",
                    "Landing page AI illimitate",
                    "Remarketing Display automatico",
                    "Tracking conversioni completo",
                    "Ottimizzazione settimanale",
                    "Report mensile",
                ],
                budget: "da \u20AC500 a \u20AC1.000/mese",
                example: "Budget \u20AC700 \u2192 \u20AC249 + \u20AC105 = \u20AC354/mese",
            },
            {
                name: "GOOGLE PRO",
                slug: "google-ads-pro",
                fee: "\u20AC399",
                percent: "12%",
                setup: "\u20AC199 setup",
                desc: "Quality Score ottimizzato, analisi competitor, dashboard live.",
                features: [
                    "Tutto di GOOGLE BASE",
                    "Controllo giornaliero campagne",
                    "Ottimizzazione attiva Quality Score",
                    "Ottimizzazione bid 3x/settimana",
                    "Dashboard live in tempo reale",
                    "Analisi competitor con review umana",
                    "Report quindicinale",
                    "Supporto chat prioritario 24h",
                    "Consulenza strategica trimestrale",
                ],
                budget: "da \u20AC1.000 a \u20AC3.000/mese",
                example: "Budget \u20AC1.500 \u2192 \u20AC399 + \u20AC180 = \u20AC579/mese",
                highlight: true,
            },
            {
                name: "GOOGLE ELITE",
                slug: "google-ads-elite",
                fee: "\u20AC649",
                percent: "10%",
                setup: "Setup incluso (min. 6 mesi)",
                desc: "Quality Score 7+, report competitor dedicato, call mensile.",
                features: [
                    "Tutto di GOOGLE PRO",
                    "Target Quality Score 7+ (-20/30% CPC)",
                    "Alert real-time + ottimizzazione quotidiana",
                    "Report competitor dedicato con analisi",
                    "Report settimanale + Dashboard live",
                    "Supporto dedicato entro 4h",
                    "Consulenza strategica mensile con call",
                ],
                budget: "da \u20AC3.000/mese in su",
                example: "Budget \u20AC4.000 \u2192 \u20AC649 + \u20AC400 = \u20AC1.049/mese",
            },
        ],
    },
    combo: {
        label: "Combo Meta + Google",
        subtitle: "Entrambi i canali, prezzo scontato",
        plans: [
            {
                name: "COMBO BASE",
                slug: "combo-ads-base",
                fee: "\u20AC379",
                percent: "14%",
                setup: "\u20AC399 setup",
                desc: "Risparmi \u20AC69/mese. Retargeting cross-platform e report unificato.",
                features: [
                    "Tutto di META BASE + GOOGLE BASE",
                    "Retargeting cross-platform",
                    "Report unificato mensile",
                    "Strategia cross-canale AI",
                    "Percentuale ridotta: 14% vs 15%",
                ],
                budget: "da \u20AC600 a \u20AC1.500/mese",
                example: "Budget \u20AC1.000 \u2192 \u20AC379 + \u20AC140 = \u20AC519/mese",
            },
            {
                name: "COMBO PRO",
                slug: "combo-ads-pro",
                fee: "\u20AC639",
                percent: "11%",
                setup: "\u20AC249 setup",
                desc: "Risparmi \u20AC109/mese. Attribution multi-touch e strategia coordinata.",
                features: [
                    "Tutto di META PRO + GOOGLE PRO",
                    "Strategia cross-canale con operatore",
                    "Retargeting cross-platform avanzato",
                    "Attribution multi-touch",
                    "Report unificato quindicinale",
                    "Call strategica trimestrale",
                    "Percentuale ridotta: 11% vs 12%",
                ],
                budget: "da \u20AC1.500 a \u20AC4.000/mese",
                example: "Budget \u20AC2.500 \u2192 \u20AC639 + \u20AC275 = \u20AC914/mese",
                highlight: true,
            },
            {
                name: "COMBO ELITE",
                slug: "combo-ads-elite",
                fee: "\u20AC999",
                percent: "9%",
                setup: "Setup incluso (min. 6 mesi)",
                desc: "Risparmi \u20AC199/mese. Account manager dedicato, la % pi\u00F9 bassa.",
                features: [
                    "Tutto di META ELITE + GOOGLE ELITE",
                    "Account manager dedicato",
                    "Attribution multi-touch avanzato",
                    "Report settimanale unificato + Call mensile",
                    "Percentuale pi\u00F9 bassa: 9%",
                ],
                budget: "da \u20AC4.000/mese in su",
                example: "Budget \u20AC5.000 \u2192 \u20AC999 + \u20AC450 = \u20AC1.449/mese",
            },
        ],
    },
};

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

// ============ HERO ============
function AdsHero() {
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    return (
        <section className="pt-32 pb-20 lg:pt-40 lg:pb-28 relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#22C55E]/20 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.6 }}>
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs uppercase font-bold tracking-widest mb-6">
                        <Megaphone className="w-3.5 h-3.5" />
                        {txt.hero.badge}
                    </div>
                    <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                        {txt.hero.title}<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22C55E] to-[#4ADE80]">{txt.hero.titleHighlight}</span>
                    </h1>
                    <p className="text-gray-400 max-w-2xl mx-auto mb-10 text-lg">
                        {txt.hero.subtitle}
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/#form-contatto"
                            className="px-8 py-4 bg-[#22C55E] hover:bg-[#16A34A] text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-green-900/40 flex items-center justify-center gap-2"
                        >
                            {txt.hero.cta} <ArrowRight className="w-5 h-5" />
                        </Link>
                        <button
                            onClick={() => document.getElementById("come-funziona-ads")?.scrollIntoView({ behavior: "smooth" })}
                            className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-bold text-lg transition-all"
                        >
                            {txt.hero.ctaSecondary}
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
                    {txt.hero.stats.map((stat, idx) => (
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
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    const serviceIcons = [Search, Megaphone, ImagePlus, BarChart3, Target, MessageSquare];

    return (
        <section className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.whatWeDo.title}
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        {txt.whatWeDo.subtitle}
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {txt.whatWeDo.services.map((service, idx) => {
                        const Icon = serviceIcons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.08 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:border-[#22C55E]/20 transition-all group"
                            >
                                <div className="w-12 h-12 rounded-xl bg-[#22C55E]/10 flex items-center justify-center mb-4 group-hover:bg-[#22C55E]/20 transition-colors">
                                    <Icon className="w-6 h-6 text-[#22C55E]" />
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
                        );
                    })}
                </div>
            </div>
        </section>
    );
}

// ============ HOW IT WORKS ============
function HowItWorks() {
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    const stepIcons = [MessageSquare, Brain, Rocket, TrendingUp];

    return (
        <section id="come-funziona-ads" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs uppercase font-bold tracking-widest mb-6">
                        <Zap className="w-3 h-3" /> {txt.howItWorks.badge}
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.howItWorks.title}<br />{txt.howItWorks.titleBreak}
                    </h2>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
                    {txt.howItWorks.steps.map((step, idx) => {
                        const Icon = stepIcons[idx];
                        const num = String(idx + 1).padStart(2, "0");
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.12 }}
                                className="relative text-center p-6"
                            >
                                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-[#22C55E]/10 border border-[#22C55E]/20 flex items-center justify-center">
                                    <Icon className="w-6 h-6 text-[#22C55E]" />
                                </div>
                                <div className="text-5xl font-bold text-white/5 mb-2">{num}</div>
                                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                                <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
                                {idx < txt.howItWorks.steps.length - 1 && (
                                    <div className="hidden lg:block absolute top-16 -right-3 text-gray-700">
                                        <ArrowRight className="w-6 h-6" />
                                    </div>
                                )}
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}

// ============ AI PIPELINE ============
function AiPipeline() {
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    const moduleIcons = [Search, BarChart3, Brain, Rocket];
    const moduleColors = ["blue", "emerald", "violet", "purple"];

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
                        <Brain className="w-3 h-3" /> {txt.aiPipeline.badge}
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.aiPipeline.title}<br />{txt.aiPipeline.titleBreak}
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        {txt.aiPipeline.subtitle}
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-6xl mx-auto">
                    {txt.aiPipeline.modules.map((module, idx) => {
                        const Icon = moduleIcons[idx];
                        const color = moduleColors[idx];
                        const colors = colorMap[color];
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
                                    <Icon className={`w-6 h-6 ${colors.text}`} />
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
                            <p className="text-sm font-bold text-white">{txt.aiPipeline.safetyTitle}</p>
                            <p className="text-xs text-gray-400 mt-1">
                                {txt.aiPipeline.safetyDesc}
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
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    const toolIcons = [ImagePlus, Video, MessageSquare];

    return (
        <section className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.contentCreation.title}<br />{txt.contentCreation.titleBreak}
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        {txt.contentCreation.subtitle}
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {txt.contentCreation.tools.map((tool, idx) => {
                        const Icon = toolIcons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                                className="p-6 rounded-2xl bg-gradient-to-b from-[#16162a] to-[#12122a] border border-white/5 text-center"
                            >
                                <div className="w-14 h-14 mx-auto rounded-2xl bg-[#22C55E]/10 flex items-center justify-center mb-4">
                                    <Icon className="w-7 h-7 text-[#22C55E]" />
                                </div>
                                <span className="inline-block text-xs px-3 py-1 rounded-full bg-[#22C55E]/10 text-[#22C55E] font-medium border border-[#22C55E]/20 mb-4">
                                    {tool.badge}
                                </span>
                                <h3 className="text-lg font-bold text-white mb-2">{tool.title}</h3>
                                <p className="text-sm text-gray-400 leading-relaxed">{tool.desc}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}

// ============ PRICING ============
function AdsPricing() {
    const [activeChannel, setActiveChannel] = useState<"meta" | "google" | "combo">("meta");
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const handleCheckout = (slug: string) => {
        if (!isAuthenticated) {
            router.push(`/auth?redirect=${encodeURIComponent(`/checkout?service=${slug}`)}`);
            return;
        }
        router.push(`/checkout?service=${slug}`);
    };

    const channels = [
        { key: "meta" as const, label: "Meta Ads", icon: Smartphone },
        { key: "google" as const, label: "Google Ads", icon: Search },
        { key: "combo" as const, label: "Combo", icon: Zap },
    ];

    const channel = ADS_CHANNELS[activeChannel];

    return (
        <section id="prezzi-ads" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        Pack Ads. Prezzi trasparenti.
                    </h2>
                    <p className="text-gray-400 text-lg mb-8">
                        Fee fisso + percentuale sul budget. L&apos;AI lavora senza limiti su ogni livello.
                    </p>

                    {/* Channel tabs */}
                    <div className="inline-flex bg-[#16162a] rounded-xl p-1 border border-white/5">
                        {channels.map((ch) => {
                            const Icon = ch.icon;
                            return (
                                <button
                                    key={ch.key}
                                    onClick={() => setActiveChannel(ch.key)}
                                    className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold transition-all ${
                                        activeChannel === ch.key
                                            ? "bg-[#22C55E] text-white shadow-lg"
                                            : "text-gray-400 hover:text-white"
                                    }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    {ch.label}
                                </button>
                            );
                        })}
                    </div>
                </motion.div>

                {/* Channel subtitle */}
                <div className="text-center mb-8">
                    <p className="text-sm text-gray-500">{channel.subtitle}</p>
                </div>

                {/* Plans grid */}
                <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-8">
                    {channel.plans.map((plan, idx) => {
                        const highlight = "highlight" in plan && plan.highlight;
                        return (
                            <motion.div
                                key={`${activeChannel}-${idx}`}
                                initial="hidden"
                                whileInView="visible"
                                viewport={{ once: true }}
                                variants={fadeUp}
                                transition={{ duration: 0.4, delay: idx * 0.1 }}
                                className={`relative p-6 rounded-2xl flex flex-col h-full transition-all ${
                                    highlight
                                        ? "bg-gradient-to-b from-[#22C55E]/15 to-[#16162a] border-2 border-[#22C55E] shadow-[0_0_40px_-10px_rgba(34,197,94,0.3)] scale-[1.02] z-10"
                                        : "bg-[#16162a] border border-white/5 hover:border-white/20"
                                }`}
                            >
                                {highlight && (
                                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#22C55E] text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                                        CONSIGLIATO
                                    </div>
                                )}

                                <div className="mb-6">
                                    <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                    <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{plan.desc}</p>
                                    <div className="flex flex-col">
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-3xl font-bold text-white tracking-tight">{plan.fee}</span>
                                            <span className="text-gray-500 text-sm">/mese</span>
                                            <span className="text-[#22C55E] text-sm font-bold">+ {plan.percent} budget</span>
                                        </div>
                                        <span className="text-xs text-gray-500 mt-1">{plan.setup}</span>
                                    </div>
                                </div>

                                <ul className="space-y-3 mb-6 flex-grow">
                                    {plan.features.map((feat, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                            <span className="text-sm text-gray-300">{feat}</span>
                                        </li>
                                    ))}
                                </ul>

                                {/* Budget example */}
                                <div className="p-3 rounded-lg bg-white/5 border border-white/5 mb-4">
                                    <p className="text-xs text-gray-500 mb-0.5">Budget consigliato: {plan.budget}</p>
                                    <p className="text-xs text-gray-300 font-medium">{plan.example}</p>
                                </div>

                                <button
                                    onClick={() => handleCheckout(plan.slug)}
                                    className={`w-full py-3 rounded-xl font-bold text-sm text-center transition-all flex items-center justify-center gap-2 ${
                                        highlight
                                            ? "bg-[#22C55E] hover:bg-[#16A34A] text-white shadow-lg"
                                            : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                    }`}
                                >
                                    Scegli {plan.name}
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Cross-sell AI Builder */}
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="max-w-3xl mx-auto mb-8">
                    <div className="flex flex-col sm:flex-row items-center gap-4 p-5 rounded-2xl bg-[#16162a] border border-[#0090FF]/20">
                        <div className="flex-grow">
                            <p className="text-sm font-bold text-white">Aggiungi un sito AI Builder e risparmi il 15%</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Starter a <span className="text-[#0090FF] font-bold">&euro;16,90/mese</span> &middot; Pro a <span className="text-[#0090FF] font-bold">&euro;33/mese</span> con qualsiasi pack Ads.
                            </p>
                        </div>
                        <button
                            onClick={() => router.push("/prezzi")}
                            className="flex items-center gap-1 px-4 py-2 rounded-lg bg-[#0090FF]/10 text-[#0090FF] text-sm font-bold border border-[#0090FF]/20 hover:bg-[#0090FF]/20 transition-all whitespace-nowrap"
                        >
                            Vedi AI Builder <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </motion.div>

                {/* Notes */}
                <div className="text-center space-x-4">
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                        Prezzi IVA esclusa
                    </span>
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                        Budget pubblicitario escluso
                    </span>
                    <span className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                        Sconto 15% pagamento annuale
                    </span>
                </div>
            </div>
        </section>
    );
}

// ============ TESTIMONIALS ============
function AdsTestimonials() {
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    return (
        <section className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-white mb-4">{txt.testimonials.title}</h2>
                </motion.div>
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {txt.testimonials.reviews.map((rev, idx) => (
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
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    return (
        <section id="faq-ads" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6 max-w-3xl">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl lg:text-4xl font-bold text-white">{txt.faq.title}</h2>
                </motion.div>

                <div className="space-y-3">
                    {txt.faq.items.map((faq, idx) => (
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
    const { language } = useLanguage();
    const txt = translations[language].adsPage;

    return (
        <section className="py-20 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#0a1a0f] to-[#0a0a1a]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#22C55E]/15 via-transparent to-transparent" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.finalCta.title}<br />{txt.finalCta.titleBreak}
                    </h2>
                    <p className="text-gray-300 mb-8 text-lg max-w-xl mx-auto">
                        {txt.finalCta.subtitle}
                    </p>
                    <Link
                        href="/#form-contatto"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-[#22C55E] hover:bg-[#16A34A] text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-green-900/40"
                    >
                        {txt.finalCta.cta} <ArrowRight className="w-5 h-5" />
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
