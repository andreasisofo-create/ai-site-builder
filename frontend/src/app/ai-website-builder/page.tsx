"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Sparkles, Zap, MessageSquare, Smartphone, Globe, Search,
    ArrowRight, Megaphone, TrendingUp, BarChart3, ChevronDown,
    Star, Check, Palette, MousePointerClick
} from "lucide-react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";
import { useLanguage, translations } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

// ============ HERO ============
function AiHero() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    return (
        <section className="pt-32 pb-20 lg:pt-40 lg:pb-28 relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.6 }}>
                    <h1 className="text-4xl lg:text-6xl font-bold text-white mb-4 leading-tight">
                        {txt.hero.title}<br />{txt.hero.titleBreak}
                    </h1>
                    <p className="text-xl text-purple-300 font-semibold mb-4">{txt.hero.subtitle}</p>
                    <p className="text-gray-400 max-w-2xl mx-auto mb-10 text-lg">
                        {txt.hero.description}
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
                        <Link
                            href="/auth"
                            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2"
                        >
                            {txt.hero.cta} <ArrowRight className="w-5 h-5" />
                        </Link>
                        <button
                            onClick={() => document.getElementById("come-funziona")?.scrollIntoView({ behavior: "smooth" })}
                            className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-bold text-lg transition-all"
                        >
                            {txt.hero.ctaSecondary}
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
                                    <Globe className="w-3 h-3" /> {txt.hero.browserUrl}
                                </div>
                            </div>
                        </div>
                        <div className="aspect-video bg-gradient-to-br from-[#16162a] to-[#0f0f1a] flex items-center justify-center relative">
                            <div className="text-center space-y-4">
                                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                                    <Sparkles className="w-8 h-8 text-purple-400" />
                                </div>
                                <p className="text-gray-500 text-sm">{txt.hero.aiCreating}</p>
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
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    const stepIcons = [MessageSquare, Sparkles, Globe];

    return (
        <section id="come-funziona" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest mb-6">
                        <Zap className="w-3 h-3" /> {txt.steps.badge}
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.steps.title}<br />{txt.steps.titleBreak}
                    </h2>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    {txt.steps.items.map((step, idx) => {
                        const Icon = stepIcons[idx];
                        const num = String(idx + 1).padStart(2, "0");
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.15 }}
                                className="text-center"
                            >
                                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                                    <Icon className="w-6 h-6 text-purple-400" />
                                </div>
                                <div className="text-5xl font-bold text-white/5 mb-2">{num}</div>
                                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                                <p className="text-sm text-gray-400 leading-relaxed">{step.desc}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}

// ============ FEATURES ============
function Features() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    const [tab, setTab] = useState<"siti" | "ads">("siti");

    const siteIcons = [Zap, Palette, MessageSquare, Smartphone, MousePointerClick, Search];
    const adsIcons = [Megaphone, TrendingUp, BarChart3, MessageSquare, Globe, Zap];

    const features = tab === "siti" ? txt.features.site : txt.features.ads;
    const icons = tab === "siti" ? siteIcons : adsIcons;

    return (
        <section id="funzionalita" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-12">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-8">
                        {txt.features.title}<br />{txt.features.titleBreak}
                    </h2>
                    {/* Toggle */}
                    <div className="inline-flex bg-white/5 rounded-full p-1 border border-white/10">
                        <button
                            onClick={() => setTab("siti")}
                            className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${tab === "siti" ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md" : "text-gray-400 hover:text-white"}`}
                        >
                            {txt.features.tabSite}
                        </button>
                        <button
                            onClick={() => setTab("ads")}
                            className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${tab === "ads" ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md" : "text-gray-400 hover:text-white"}`}
                        >
                            {txt.features.tabAds}
                        </button>
                    </div>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {features.map((feat, idx) => {
                        const Icon = icons[idx];
                        return (
                            <motion.div
                                key={`${tab}-${idx}`}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: idx * 0.08 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5 hover:border-purple-500/20 transition-all"
                            >
                                <Icon className="w-6 h-6 text-purple-400 mb-3" />
                                <h3 className="font-bold text-white mb-1">{feat.title}</h3>
                                <p className="text-sm text-gray-400">{feat.desc}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}

// ============ ADS SECTION ============
function AdsSection() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    const cardIcons = [Megaphone, Search, BarChart3];

    return (
        <section id="servizio-ads" className="py-20 lg:py-28 bg-[#0f0f23] relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent pointer-events-none" />
            <div className="container mx-auto px-6 relative z-10">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest mb-6">
                        <TrendingUp className="w-3 h-3" /> {txt.adsSection.badge}
                    </div>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.adsSection.title}<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">{txt.adsSection.titleHighlight}</span>
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                        {txt.adsSection.subtitle}
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-12">
                    {txt.adsSection.cards.map((card, idx) => {
                        const Icon = cardIcons[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.5, delay: idx * 0.1 }}
                                className="p-6 rounded-2xl bg-[#16162a] border border-white/5"
                            >
                                <Icon className="w-8 h-8 text-purple-400 mb-4" />
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
                        );
                    })}
                </div>

                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center">
                    <div className="inline-block p-6 rounded-2xl bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/20">
                        <p className="text-sm text-gray-300 mb-1"><strong>{txt.adsSection.flowTitle}</strong></p>
                        <p className="text-xs text-gray-500">
                            {txt.adsSection.flowDesc}
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

// ============ PORTFOLIO ============
function AiPortfolio() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

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
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">{txt.portfolio.title}</h2>
                    <p className="text-gray-400">{txt.portfolio.subtitle}</p>
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
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    return (
        <section className="py-20 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    {txt.testimonials.map((rev, idx) => (
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
// Slug mapping for the AI builder plans (order matches translations.aiPage.pricing.plans)
// Maps to actual service catalog slugs: pack-presenza, pack-clienti, pack-crescita
const AI_BASE_SLUG = "homepage-ai";
const AI_PLAN_SLUGS = ["pack-presenza", "pack-clienti", "pack-crescita"];

function AiPricing() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const handleCheckout = (slug: string) => {
        if (!isAuthenticated) {
            router.push(`/auth?redirect=${encodeURIComponent(`/checkout?service=${slug}`)}`);
            return;
        }
        router.push(`/checkout?service=${slug}`);
    };

    return (
        <section id="prezzi-ai" className="py-20 lg:py-28 bg-[#0a0a1a]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.pricing.title}<br />{txt.pricing.titleBreak}
                    </h2>
                    <p className="text-gray-400 text-lg">
                        {txt.pricing.subtitle}
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
                            <Globe className="w-3.5 h-3.5" /> {txt.pricing.baseBadge}
                        </span>
                    </div>
                    <div className="relative p-8 rounded-2xl bg-gradient-to-br from-[#0090FF]/20 via-[#0060CC]/10 to-[#16162a] border-2 border-[#0090FF]/40 shadow-[0_0_50px_-15px_rgba(0,144,255,0.3)]">
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                            <div className="flex-1">
                                <h3 className="text-2xl font-bold text-white mb-2">{txt.pricing.baseName}</h3>
                                <p className="text-gray-300 mb-4">{txt.pricing.baseDesc}</p>
                                <ul className="grid grid-cols-2 gap-2">
                                    {txt.pricing.baseFeatures.map((feat, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <Check className="w-4 h-4 text-[#0090FF] mt-0.5 flex-shrink-0" />
                                            <span className="text-sm text-gray-300">{feat}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="text-center md:text-right flex flex-col items-center md:items-end gap-3 md:min-w-[180px]">
                                <div>
                                    <span className="text-4xl font-bold text-white">{txt.pricing.basePrice}</span>
                                    <span className="text-gray-400 ml-1 text-sm">{txt.pricing.basePeriod}</span>
                                </div>
                                <span className="text-xs text-[#0090FF] font-semibold">{txt.pricing.baseNoCost}</span>
                                <button
                                    onClick={() => handleCheckout(AI_BASE_SLUG)}
                                    className="px-8 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-bold text-sm transition-all shadow-lg shadow-blue-900/30 block"
                                >
                                    {txt.pricing.baseCta}
                                </button>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Divider */}
                <div className="max-w-4xl mx-auto mb-12 flex items-center gap-4">
                    <div className="flex-1 h-px bg-white/10" />
                    <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs uppercase font-bold tracking-widest">
                        <TrendingUp className="w-3.5 h-3.5" /> {txt.pricing.divider}
                    </span>
                    <div className="flex-1 h-px bg-white/10" />
                </div>

                {/* ADS PLANS - 3 cards */}
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-8">
                    {txt.pricing.plans.map((plan, idx) => {
                        const highlight = "tag" in plan && !!plan.tag;
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.4, delay: idx * 0.1 }}
                                className={`relative p-6 rounded-2xl flex flex-col h-full transition-all ${highlight
                                        ? "bg-gradient-to-b from-purple-900/40 to-[#16162a] border-2 border-purple-500 shadow-[0_0_40px_-10px_rgba(147,51,234,0.3)] scale-[1.02] z-10"
                                        : "bg-[#16162a] border border-white/5 hover:border-white/20"
                                    }`}
                            >
                                {highlight && "tag" in plan && (
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
                                <button
                                    onClick={() => handleCheckout(AI_PLAN_SLUGS[idx])}
                                    className={`w-full py-3 rounded-xl font-bold text-sm text-center transition-all block ${highlight
                                            ? "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg"
                                            : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                        }`}
                                >
                                    {plan.cta}
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                <div className="text-center text-sm text-gray-500">
                    {txt.pricing.budgetNote}
                </div>
            </div>
        </section>
    );
}

// ============ FAQ ============
function AiFaq() {
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section id="faq-ai" className="py-20 lg:py-28 bg-[#0f0f23]">
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
    const { language } = useLanguage();
    const txt = translations[language].aiPage;

    return (
        <section className="py-20 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-900/60 to-blue-900/60" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-600/20 via-transparent to-transparent" />
            <div className="container mx-auto px-6 relative z-10 text-center">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.finalCta.title}<br />{txt.finalCta.titleBreak}
                    </h2>
                    <p className="text-gray-300 mb-8 text-lg">
                        {txt.finalCta.subtitle}
                    </p>
                    <Link
                        href="/auth"
                        className="inline-flex items-center gap-2 px-8 py-4 bg-white text-[#0a0a1a] rounded-xl font-bold text-lg hover:bg-gray-100 transition-all shadow-lg"
                    >
                        {txt.finalCta.cta} <Sparkles className="w-5 h-5 text-purple-600" />
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
