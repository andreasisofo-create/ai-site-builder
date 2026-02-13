"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useEffect } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  Play,
  MessageSquare,
  Sparkles,
  Globe,
  ChevronDown,
  Check,
  Menu,
  X,
  Smartphone,
  MousePointerClick,
  Search,
  Megaphone,
  BarChart3,
  Video,
  Users,
  FileText,
  Wallet,
  Star,
  Zap,
  Shield,
  Target,
} from "lucide-react";
import { translations } from "@/lib/i18n";
import { useRef } from "react";

// ==================== DATA ====================

const tx = translations.it;

// ==================== ANIMATION HELPERS ====================

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

// ==================== MAIN PAGE ====================

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"site" | "clients">("site");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const howRef = useRef(null);
  const howInView = useInView(howRef, { once: true, margin: "-80px" });
  const featRef = useRef(null);
  const featInView = useInView(featRef, { once: true, margin: "-80px" });
  const adsRef = useRef(null);
  const adsInView = useInView(adsRef, { once: true, margin: "-80px" });
  const proofRef = useRef(null);
  const proofInView = useInView(proofRef, { once: true, margin: "-80px" });
  const priceRef = useRef(null);
  const priceInView = useInView(priceRef, { once: true, margin: "-80px" });

  const stepIcons = [MessageSquare, Sparkles, Globe];
  const stepNumbers = ["01", "02", "03"];

  const siteIcons = [Sparkles, MousePointerClick, MessageSquare, Smartphone, Globe, Search];
  const clientIcons = [Megaphone, Search, Video, Users, BarChart3, Wallet];

  const activeFeatures = activeTab === "site" ? tx.features.site : tx.features.clients;
  const activeIcons = activeTab === "site" ? siteIcons : clientIcons;

  const adsColumnIcons = [Megaphone, Target, BarChart3];
  const adsFlowIcons = [Zap, Shield, BarChart3];

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-x-hidden">
      {/* ===== NAVBAR ===== */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? "bg-white/80 backdrop-blur-xl border-b border-slate-200 shadow-sm"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link href="/" className="flex items-center">
              <Image
                src="/e-quipe-logo-dark.png"
                alt="E-quipe"
                width={140}
                height={40}
                className="h-9 w-auto"
              />
            </Link>

            <div className="hidden lg:flex items-center gap-8">
              <a
                href="#come-funziona"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                {tx.nav.howItWorks}
              </a>
              <a
                href="#funzionalita"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                {tx.nav.features}
              </a>
              <a
                href="#ads-service"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                Servizio Ads
              </a>
              <a
                href="#prezzi"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                {tx.nav.pricing}
              </a>
              <a
                href="#faq"
                className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                {tx.nav.faq}
              </a>
            </div>

            <div className="hidden lg:flex items-center gap-3">
              <Link
                href="/auth"
                className="px-5 py-2.5 text-sm font-semibold text-white rounded-full transition-all duration-200 hover:opacity-90 shadow-md shadow-indigo-500/25"
                style={{
                  background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                }}
              >
                {tx.nav.cta}
              </Link>
            </div>

            <button
              className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6 text-slate-700" />
              ) : (
                <Menu className="w-6 h-6 text-slate-700" />
              )}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden bg-white/95 backdrop-blur-xl border-b border-slate-200 overflow-hidden"
            >
              <div className="px-6 py-4 space-y-4">
                <a
                  href="#come-funziona"
                  className="block text-slate-600 hover:text-slate-900 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {tx.nav.howItWorks}
                </a>
                <a
                  href="#funzionalita"
                  className="block text-slate-600 hover:text-slate-900 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {tx.nav.features}
                </a>
                <a
                  href="#ads-service"
                  className="block text-slate-600 hover:text-slate-900 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Servizio Ads
                </a>
                <a
                  href="#prezzi"
                  className="block text-slate-600 hover:text-slate-900 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {tx.nav.pricing}
                </a>
                <a
                  href="#faq"
                  className="block text-slate-600 hover:text-slate-900 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {tx.nav.faq}
                </a>
                <hr className="border-slate-200" />
                <Link
                  href="/auth"
                  className="block w-full py-3 text-white rounded-full font-semibold text-center"
                  style={{
                    background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                  }}
                >
                  {tx.nav.cta}
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ===== HERO ===== */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-28 overflow-hidden"
        style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(79,70,229,0.08) 0%, rgba(124,58,237,0.04) 40%, white 70%)" }}
      >
        {/* Decorative gradient orbs */}
        <div className="absolute top-[-200px] left-[-100px] w-[600px] h-[600px] rounded-full opacity-[0.15] pointer-events-none"
          style={{ background: "radial-gradient(circle, #4F46E5, transparent 70%)", filter: "blur(80px)" }}
        />
        <div className="absolute top-[-100px] right-[-150px] w-[500px] h-[500px] rounded-full opacity-[0.12] pointer-events-none"
          style={{ background: "radial-gradient(circle, #7C3AED, transparent 70%)", filter: "blur(80px)" }}
        />
        <div className="absolute bottom-[-100px] left-[30%] w-[400px] h-[400px] rounded-full opacity-[0.08] pointer-events-none"
          style={{ background: "radial-gradient(circle, #06B6D4, transparent 70%)", filter: "blur(60px)" }}
        />

        <div className="max-w-7xl mx-auto px-6 relative">
          <div className="max-w-3xl mx-auto text-center">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight text-slate-900 mb-4"
            >
              {tx.hero.title}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.12, ease: "easeOut" }}
              className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6"
              style={{
                background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              {tx.hero.subtitle}
            </motion.p>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.24, ease: "easeOut" }}
              className="text-lg text-slate-500 max-w-2xl mx-auto mb-10 leading-relaxed"
            >
              {tx.hero.description}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.36, ease: "easeOut" }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link
                href="/auth"
                className="group w-full sm:w-auto px-8 py-4 text-white rounded-full font-semibold text-lg hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center gap-2"
                style={{
                  background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                  boxShadow: "0 8px 32px rgba(79, 70, 229, 0.35), 0 2px 8px rgba(79, 70, 229, 0.2)",
                }}
              >
                {tx.hero.cta}
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="#come-funziona"
                className="group w-full sm:w-auto px-8 py-4 text-slate-700 bg-white border border-slate-200 rounded-full font-semibold text-lg hover:border-indigo-200 hover:bg-indigo-50/50 transition-all flex items-center justify-center gap-2"
                style={{ boxShadow: "0 4px 16px rgba(0, 0, 0, 0.06)" }}
              >
                <Play className="w-5 h-5 text-indigo-600" />
                {tx.hero.ctaSecondary}
              </a>
            </motion.div>
          </div>

          {/* Hero Video */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease: "easeOut" }}
            className="mt-16 max-w-4xl mx-auto"
          >
            <div
              className="relative aspect-video rounded-2xl overflow-hidden"
              style={{
                border: "1px solid rgba(79, 70, 229, 0.15)",
                boxShadow: "0 20px 60px rgba(79, 70, 229, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08)",
              }}
            >
              <video
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover"
              >
                <source src="/videos/hero.mp4" type="video/mp4" />
              </video>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== COME FUNZIONA ===== */}
      <section
        id="come-funziona"
        className="py-20 lg:py-28 relative"
        style={{ background: "linear-gradient(180deg, #F8FAFC 0%, rgba(238, 242, 255, 0.3) 50%, #F8FAFC 100%)" }}
        ref={howRef}
      >
        {/* Subtle decorative line */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-20 bg-gradient-to-b from-transparent via-indigo-200 to-transparent" />

        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={howInView ? "visible" : "hidden"}
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <span
              className="inline-block px-4 py-1.5 rounded-full text-sm font-medium mb-6"
              style={{
                background: "linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.1))",
                color: "#4F46E5",
                border: "1px solid rgba(79, 70, 229, 0.15)",
              }}
            >
              {tx.howItWorks.label}
            </span>
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-slate-900">
              {tx.howItWorks.title}
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {tx.howItWorks.steps.map((step, idx) => {
              const Icon = stepIcons[idx];
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 32 }}
                  animate={howInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: idx * 0.15 }}
                  className="relative bg-white rounded-2xl p-8 group hover:-translate-y-1 transition-all duration-300"
                  style={{
                    border: "1px solid rgba(79, 70, 229, 0.1)",
                    boxShadow: "0 4px 24px rgba(79, 70, 229, 0.06)",
                  }}
                >
                  {/* Gradient border on hover */}
                  <div
                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                    style={{
                      padding: "1px",
                      background: "linear-gradient(135deg, rgba(79, 70, 229, 0.3), rgba(124, 58, 237, 0.2), rgba(6, 182, 212, 0.2))",
                      mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                      maskComposite: "exclude",
                      WebkitMaskComposite: "xor",
                    }}
                  />
                  <span className="absolute top-6 right-6 text-5xl font-black text-slate-100/80">
                    {stepNumbers[idx]}
                  </span>
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
                    style={{
                      background: "linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.1))",
                    }}
                  >
                    <Icon className="w-6 h-6 text-indigo-600" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    {step.title}
                  </h3>
                  <p className="text-slate-500 text-sm leading-relaxed">
                    {step.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ===== FUNZIONALITA' ===== */}
      <section id="funzionalita" className="py-20 lg:py-28 bg-white relative" ref={featRef}>
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={featInView ? "visible" : "hidden"}
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl mx-auto mb-12"
          >
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-slate-900 mb-6">
              {tx.features.title}
            </h2>

            {/* Tabs */}
            <div
              className="inline-flex items-center gap-1 p-1 rounded-full border"
              style={{
                backgroundColor: "rgba(248, 250, 252, 0.8)",
                borderColor: "rgba(79, 70, 229, 0.1)",
              }}
            >
              <button
                onClick={() => setActiveTab("site")}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  activeTab === "site"
                    ? "text-white shadow-md"
                    : "text-slate-500 hover:text-slate-700"
                }`}
                style={
                  activeTab === "site"
                    ? { background: "linear-gradient(135deg, #4F46E5, #7C3AED)" }
                    : undefined
                }
              >
                {tx.features.tabs.site}
              </button>
              <button
                onClick={() => setActiveTab("clients")}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  activeTab === "clients"
                    ? "text-white shadow-md"
                    : "text-slate-500 hover:text-slate-700"
                }`}
                style={
                  activeTab === "clients"
                    ? { background: "linear-gradient(135deg, #4F46E5, #7C3AED)" }
                    : undefined
                }
              >
                {tx.features.tabs.clients}
              </button>
            </div>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {activeFeatures.map((feat, idx) => {
              const Icon = activeIcons[idx];
              return (
                <motion.div
                  key={`${activeTab}-${idx}`}
                  initial={{ opacity: 0, y: 24 }}
                  animate={featInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.4, delay: idx * 0.08 }}
                  className="group relative rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1"
                  style={{
                    background: "rgba(255, 255, 255, 0.8)",
                    backdropFilter: "blur(12px)",
                    border: "1px solid rgba(79, 70, 229, 0.08)",
                    boxShadow: "0 4px 24px rgba(79, 70, 229, 0.04)",
                  }}
                >
                  {/* Hover gradient border */}
                  <div
                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                    style={{
                      padding: "1px",
                      background: "linear-gradient(135deg, rgba(79, 70, 229, 0.25), rgba(124, 58, 237, 0.15), rgba(16, 185, 129, 0.15))",
                      mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                      maskComposite: "exclude",
                      WebkitMaskComposite: "xor",
                    }}
                  />
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                    style={{
                      background: "linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(124, 58, 237, 0.08))",
                    }}
                  >
                    <Icon className="w-5 h-5 text-indigo-600" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-1.5">
                    {feat.title}
                  </h3>
                  <p className="text-slate-500 text-sm leading-relaxed">
                    {feat.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ===== ADS SERVICE SECTION ===== */}
      <section
        id="ads-service"
        className="py-20 lg:py-28 relative overflow-hidden"
        ref={adsRef}
        style={{
          background: "linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4c1d95 60%, #1e1b4b 100%)",
        }}
      >
        {/* Decorative glowing orbs */}
        <div className="absolute top-[-150px] right-[-100px] w-[500px] h-[500px] rounded-full opacity-20 pointer-events-none"
          style={{ background: "radial-gradient(circle, #7C3AED, transparent 70%)", filter: "blur(80px)" }}
        />
        <div className="absolute bottom-[-100px] left-[-100px] w-[400px] h-[400px] rounded-full opacity-15 pointer-events-none"
          style={{ background: "radial-gradient(circle, #4F46E5, transparent 70%)", filter: "blur(60px)" }}
        />

        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.05]"
          style={{
            backgroundImage: "linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />

        <div className="max-w-7xl mx-auto px-6 relative">
          {/* Section Header */}
          <motion.div
            initial="hidden"
            animate={adsInView ? "visible" : "hidden"}
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <span
              className="inline-block px-4 py-1.5 rounded-full text-sm font-medium mb-6"
              style={{
                background: "rgba(255, 255, 255, 0.1)",
                color: "rgba(196, 181, 253, 1)",
                border: "1px solid rgba(139, 92, 246, 0.3)",
              }}
            >
              {tx.ads.badge}
            </span>
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-white mb-4">
              {tx.ads.title}
              <br />
              <span
                style={{
                  background: "linear-gradient(135deg, #a78bfa, #c084fc, #f472b6)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {tx.ads.titleHighlight}
              </span>
            </h2>
            <p className="text-lg text-slate-300">
              {tx.ads.subtitle}
            </p>
          </motion.div>

          {/* Three columns */}
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-16">
            {tx.ads.columns.map((col, idx) => {
              const Icon = adsColumnIcons[idx];
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 32 }}
                  animate={adsInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: idx * 0.15 }}
                  className="rounded-2xl p-6 group hover:-translate-y-1 transition-all duration-300"
                  style={{
                    background: "rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(12px)",
                    border: "1px solid rgba(139, 92, 246, 0.2)",
                    boxShadow: "0 4px 24px rgba(0, 0, 0, 0.2)",
                  }}
                >
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                    style={{
                      background: "linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(124, 58, 237, 0.2))",
                    }}
                  >
                    <Icon className="w-6 h-6 text-violet-300" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-1">{col.title}</h3>
                  <p className="text-sm text-violet-300 mb-4">{col.subtitle}</p>
                  <ul className="space-y-2.5">
                    {col.items.map((item, iIdx) => (
                      <li key={iIdx} className="flex items-start gap-2.5">
                        <Check className="w-4 h-4 text-violet-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-slate-300">{item}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              );
            })}
          </div>

          {/* Flow / Process */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={adsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="max-w-3xl mx-auto"
          >
            <h3 className="text-center text-lg font-bold text-white mb-8">
              {tx.ads.flowTitle}
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-6">
              {tx.ads.flowSteps.map((step, idx) => {
                const FlowIcon = adsFlowIcons[idx];
                return (
                  <div key={idx} className="flex items-center gap-4 md:gap-6">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                        style={{
                          background: "linear-gradient(135deg, rgba(139, 92, 246, 0.4), rgba(79, 70, 229, 0.3))",
                          border: "1px solid rgba(139, 92, 246, 0.4)",
                        }}
                      >
                        <FlowIcon className="w-5 h-5 text-violet-300" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-white">{step.title}</p>
                        <p className="text-xs text-violet-300">{step.subtitle}</p>
                      </div>
                    </div>
                    {idx < 2 && (
                      <ArrowRight className="hidden md:block w-5 h-5 text-violet-500/50 flex-shrink-0" />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Compliance badge */}
            <div className="mt-10 text-center">
              <span
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs"
                style={{
                  background: "rgba(16, 185, 129, 0.1)",
                  border: "1px solid rgba(16, 185, 129, 0.25)",
                  color: "#6ee7b7",
                }}
              >
                <Shield className="w-3.5 h-3.5" />
                {tx.ads.complianceBadge}
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== SOCIAL PROOF ===== */}
      <section
        className="py-20 lg:py-28 relative"
        style={{
          background: "linear-gradient(180deg, #F8FAFC 0%, rgba(248, 250, 252, 0.5) 50%, white 100%)",
        }}
        ref={proofRef}
      >
        {/* Subtle decorative dots */}
        <div className="absolute top-20 right-10 w-32 h-32 opacity-[0.04] pointer-events-none"
          style={{
            backgroundImage: "radial-gradient(circle, #4F46E5 1px, transparent 1px)",
            backgroundSize: "12px 12px",
          }}
        />

        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={proofInView ? "visible" : "hidden"}
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
              {tx.socialProof.title}
            </h2>
            <p className="text-lg text-slate-500">{tx.socialProof.subtitle}</p>
          </motion.div>

          {/* Demo Site Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-5 max-w-5xl mx-auto mb-16">
            {tx.socialProof.demos.map((demo, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 24 }}
                animate={proofInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                className="bg-white rounded-2xl overflow-hidden group hover:-translate-y-1 transition-all duration-300"
                style={{
                  border: "1px solid rgba(79, 70, 229, 0.08)",
                  boxShadow: "0 8px 32px rgba(79, 70, 229, 0.06), 0 2px 8px rgba(0, 0, 0, 0.04)",
                }}
              >
                <div className="aspect-[4/3] bg-slate-50 overflow-hidden">
                  <Image
                    src={demo.image}
                    alt={demo.name}
                    width={600}
                    height={450}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-4">
                  <p className="font-semibold text-sm text-slate-900">
                    {demo.name}
                  </p>
                  <p className="text-xs text-slate-400">{demo.category}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Testimonials */}
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {tx.socialProof.testimonials.map((t, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 24 }}
                animate={proofInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.4, delay: 0.4 + idx * 0.12 }}
                className="bg-white rounded-2xl p-6"
                style={{
                  border: "1px solid rgba(79, 70, 229, 0.08)",
                  boxShadow: "0 8px 32px rgba(79, 70, 229, 0.06), 0 2px 8px rgba(0, 0, 0, 0.04)",
                }}
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className="w-4 h-4 text-amber-400 fill-amber-400"
                    />
                  ))}
                </div>
                <p className="text-slate-700 text-sm leading-relaxed mb-5">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs"
                    style={{
                      background: "linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(124, 58, 237, 0.15))",
                      color: "#4F46E5",
                    }}
                  >
                    {t.author
                      .split(" ")
                      .map((w) => w[0])
                      .join("")}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">
                      {t.author}
                    </p>
                    <p className="text-xs text-slate-400">{t.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PRICING ===== */}
      <section id="prezzi" className="py-20 lg:py-28 bg-white relative" ref={priceRef}>
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={priceInView ? "visible" : "hidden"}
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
              {tx.pricing.title}
            </h2>
            <p className="text-lg text-slate-500">{tx.pricing.subtitle}</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-6xl mx-auto">
            {tx.pricing.plans.map((plan, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 24 }}
                animate={priceInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className={`relative rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 ${
                  plan.popular ? "bg-white" : "bg-white"
                }`}
                style={
                  plan.popular
                    ? {
                        border: "1px solid rgba(79, 70, 229, 0.3)",
                        boxShadow: "0 20px 60px rgba(79, 70, 229, 0.15), 0 8px 24px rgba(79, 70, 229, 0.1)",
                      }
                    : {
                        border: "1px solid rgba(79, 70, 229, 0.08)",
                        boxShadow: "0 4px 24px rgba(0, 0, 0, 0.04)",
                      }
                }
              >
                {/* Gradient glow behind popular plan */}
                {plan.popular && (
                  <>
                    <div
                      className="absolute -inset-[1px] rounded-2xl -z-10"
                      style={{
                        background: "linear-gradient(135deg, #4F46E5, #7C3AED, #4F46E5)",
                        filter: "blur(8px)",
                        opacity: 0.3,
                      }}
                    />
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span
                        className="px-4 py-1 text-xs font-bold text-white rounded-full"
                        style={{
                          background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                          boxShadow: "0 4px 12px rgba(79, 70, 229, 0.4)",
                        }}
                      >
                        Consigliato
                      </span>
                    </div>
                  </>
                )}

                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    {plan.name}
                  </h3>
                  <p className="text-xs text-slate-400">{plan.description}</p>
                </div>

                <div className="mb-5">
                  <span className="text-4xl font-bold text-slate-900">
                    &euro;{plan.price}
                  </span>
                  <span className="text-slate-400 ml-1 text-sm">
                    {plan.period}
                  </span>
                </div>

                <ul className="space-y-2.5 mb-6">
                  {plan.features.map((feature, fidx) => (
                    <li
                      key={fidx}
                      className="flex items-start gap-2.5 text-slate-600"
                    >
                      <Check className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/auth"
                  className={`block w-full py-3 rounded-full font-semibold text-sm text-center transition-all ${
                    plan.popular
                      ? "text-white hover:opacity-90"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                  style={
                    plan.popular
                      ? {
                          background: "linear-gradient(135deg, #4F46E5, #7C3AED)",
                          boxShadow: "0 4px 16px rgba(79, 70, 229, 0.35)",
                        }
                      : {
                          background: "rgba(248, 250, 252, 0.8)",
                          border: "1px solid rgba(79, 70, 229, 0.1)",
                        }
                  }
                >
                  {plan.cta}
                </Link>
              </motion.div>
            ))}
          </div>

          <p className="text-center text-sm text-slate-400 mt-8">
            {tx.pricing.adBudgetNote}
          </p>
        </div>
      </section>

      {/* ===== FAQ ===== */}
      <section
        id="faq"
        className="py-20 lg:py-28 relative"
        style={{
          background: "linear-gradient(180deg, #F8FAFC 0%, rgba(238, 242, 255, 0.2) 50%, #F8FAFC 100%)",
        }}
      >
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-slate-900">
              {tx.faq.title}
            </h2>
          </div>

          <div className="space-y-3">
            {tx.faq.items.map((faq, idx) => (
              <div
                key={idx}
                className="rounded-2xl bg-white overflow-hidden transition-all"
                style={{
                  border: "1px solid rgba(79, 70, 229, 0.08)",
                  boxShadow: openFaq === idx ? "0 8px 32px rgba(79, 70, 229, 0.08)" : "0 2px 8px rgba(0, 0, 0, 0.02)",
                }}
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-indigo-50/30 transition-colors"
                >
                  <span className="font-medium text-slate-900 pr-4">
                    {faq.q}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-slate-400 flex-shrink-0 transition-transform duration-300 ${
                      openFaq === idx ? "rotate-180" : ""
                    }`}
                  />
                </button>
                <AnimatePresence>
                  {openFaq === idx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-5 text-slate-500 leading-relaxed text-sm">
                        {faq.a}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="py-20 lg:py-28 bg-white">
        <div className="max-w-4xl mx-auto px-6">
          <div
            className="relative p-12 lg:p-20 rounded-3xl overflow-hidden text-center"
            style={{
              background: "linear-gradient(135deg, #312e81 0%, #4c1d95 50%, #1e1b4b 100%)",
            }}
          >
            {/* Decorative orbs inside CTA */}
            <div className="absolute top-[-60px] right-[-60px] w-[200px] h-[200px] rounded-full opacity-30 pointer-events-none"
              style={{ background: "radial-gradient(circle, #7C3AED, transparent 70%)", filter: "blur(40px)" }}
            />
            <div className="absolute bottom-[-40px] left-[-40px] w-[180px] h-[180px] rounded-full opacity-25 pointer-events-none"
              style={{ background: "radial-gradient(circle, #4F46E5, transparent 70%)", filter: "blur(40px)" }}
            />

            <div className="relative">
              <h2 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-white mb-4">
                Pronto a portare la tua attivita&apos; online?
              </h2>
              <p className="text-lg text-indigo-200 mb-8 max-w-xl mx-auto">
                Crea il tuo sito in 60 secondi. Gratis, senza carta di credito.
              </p>
              <Link
                href="/auth"
                className="group inline-flex items-center gap-2 px-8 py-4 text-slate-900 rounded-full font-semibold text-lg hover:-translate-y-0.5 transition-all duration-200"
                style={{
                  background: "linear-gradient(135deg, #ffffff, #e0e7ff)",
                  boxShadow: "0 8px 32px rgba(255, 255, 255, 0.25), 0 2px 8px rgba(255, 255, 255, 0.15)",
                }}
              >
                Crea il tuo sito gratis
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="py-16 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-5 gap-8 mb-12">
            {/* Brand */}
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center mb-4">
                <Image
                  src="/e-quipe-logo-dark.png"
                  alt="E-quipe"
                  width={120}
                  height={36}
                  className="h-8 w-auto"
                />
              </Link>
              <p className="text-slate-500 text-sm max-w-sm">
                {tx.footer.description}
              </p>
            </div>

            {/* Prodotto */}
            <div>
              <h4 className="font-semibold text-slate-900 mb-4 text-sm">
                {tx.footer.product}
              </h4>
              <ul className="space-y-2.5 text-slate-500 text-sm">
                <li>
                  <a
                    href="#come-funziona"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.productLinks.howItWorks}
                  </a>
                </li>
                <li>
                  <a
                    href="#funzionalita"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.productLinks.features}
                  </a>
                </li>
                <li>
                  <a
                    href="#prezzi"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.productLinks.pricing}
                  </a>
                </li>
                <li>
                  <Link
                    href="/dashboard"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.productLinks.dashboard}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Azienda */}
            <div>
              <h4 className="font-semibold text-slate-900 mb-4 text-sm">
                {tx.footer.company}
              </h4>
              <ul className="space-y-2.5 text-slate-500 text-sm">
                <li>
                  <a href="#" className="hover:text-slate-900 transition-colors">
                    {tx.footer.companyLinks.about}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-slate-900 transition-colors">
                    {tx.footer.companyLinks.contact}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-slate-900 transition-colors">
                    {tx.footer.companyLinks.blog}
                  </a>
                </li>
              </ul>
            </div>

            {/* Legale */}
            <div>
              <h4 className="font-semibold text-slate-900 mb-4 text-sm">
                {tx.footer.legal}
              </h4>
              <ul className="space-y-2.5 text-slate-500 text-sm">
                <li>
                  <Link
                    href="/privacy"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.legalLinks.privacy}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/terms"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.legalLinks.terms}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/cookies"
                    className="hover:text-slate-900 transition-colors"
                  >
                    {tx.footer.legalLinks.cookies}
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-400 text-sm">{tx.footer.copyright}</p>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <Link
                href="/privacy"
                className="hover:text-slate-700 transition-colors"
              >
                Privacy
              </Link>
              <Link
                href="/terms"
                className="hover:text-slate-700 transition-colors"
              >
                Termini
              </Link>
              <Link
                href="/cookies"
                className="hover:text-slate-700 transition-colors"
              >
                Cookie
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
