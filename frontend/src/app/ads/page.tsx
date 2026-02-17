"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Megaphone, TrendingUp, BarChart3, Search, Target, Zap,
    Check, ChevronDown, Star, ArrowRight, Shield, Brain,
    Rocket, MessageSquare, ImagePlus, Video, Globe,
    Smartphone, DollarSign, Users, Clock, Eye, Loader2
} from "lucide-react";
import toast from "react-hot-toast";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";
import { useLanguage, translations } from "@/lib/i18n";
import { checkoutService } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

// Pack slug mapping (order matches translations.adsPage.pricing.packs)
const PACK_SLUGS = ["pack-presenza", "pack-clienti", "pack-crescita", "pack-premium"];

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
    const { language } = useLanguage();
    const txt = translations[language].adsPage;
    const router = useRouter();
    const { isAuthenticated } = useAuth();
    const [loadingSlug, setLoadingSlug] = useState<string | null>(null);

    const handleCheckout = async (slug: string) => {
        if (!isAuthenticated) {
            router.push(`/auth?redirect=/ads&service=${slug}`);
            return;
        }

        setLoadingSlug(slug);
        try {
            const result = await checkoutService(slug);
            if (result.checkout_url) {
                window.location.href = result.checkout_url;
            } else if (result.activated) {
                toast.success(language === "it" ? "Servizio attivato con successo!" : "Service activated successfully!");
                router.push("/dashboard");
            } else {
                toast.success(language === "it" ? "Ordine creato. Completa il pagamento." : "Order created. Complete the payment.");
            }
        } catch (error: any) {
            toast.error(error.message || (language === "it" ? "Errore durante il checkout. Riprova." : "Checkout error. Please try again."));
        } finally {
            setLoadingSlug(null);
        }
    };

    return (
        <section id="prezzi-ads" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} className="text-center mb-16">
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">
                        {txt.pricing.title}
                    </h2>
                    <p className="text-gray-400 text-lg">
                        {txt.pricing.subtitle}
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-8">
                    {txt.pricing.packs.map((plan, idx) => {
                        const highlight = idx === 2;
                        const tag = "tag" in plan ? plan.tag : undefined;
                        const slug = PACK_SLUGS[idx];
                        return (
                            <motion.div
                                key={idx}
                                initial="hidden" whileInView="visible" viewport={{ once: true }}
                                variants={fadeUp} transition={{ duration: 0.4, delay: idx * 0.1 }}
                                className={`relative p-6 rounded-2xl flex flex-col h-full transition-all ${highlight
                                    ? "bg-gradient-to-b from-[#22C55E]/15 to-[#16162a] border-2 border-[#22C55E] shadow-[0_0_40px_-10px_rgba(34,197,94,0.3)] scale-[1.02] z-10"
                                    : "bg-[#16162a] border border-white/5 hover:border-white/20"
                                    }`}
                            >
                                {highlight && tag && (
                                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#22C55E] text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                                        {tag}
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
                                <button
                                    onClick={() => handleCheckout(slug)}
                                    disabled={loadingSlug !== null}
                                    className={`w-full py-3 rounded-xl font-bold text-sm text-center transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed ${highlight
                                        ? "bg-[#22C55E] hover:bg-[#16A34A] text-white shadow-lg"
                                        : "bg-white/5 hover:bg-white/10 text-white border border-white/10"
                                        }`}
                                >
                                    {loadingSlug === slug ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            {language === "it" ? "Caricamento..." : "Loading..."}
                                        </>
                                    ) : (
                                        txt.pricing.packs[idx].cta
                                    )}
                                </button>
                            </motion.div>
                        );
                    })}
                </div>

                <div className="text-center space-x-4">
                    {txt.pricing.notes.map((note, idx) => (
                        <span key={idx} className="text-sm text-gray-500 bg-[#16162a] px-4 py-2 rounded-full border border-white/5">
                            {note}
                        </span>
                    ))}
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
