"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";
import LanguageSwitcher from "@/components/LanguageSwitcher";

interface NavbarProps {
    variant?: "agency" | "ai";
}

export default function Navbar({ variant = "agency" }: NavbarProps) {
    const { language } = useLanguage();
    const nav = translations[language].nav;
    const pathname = usePathname();
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const isOnAiPage = pathname === "/ai-website-builder";
    const isOnAdsPage = pathname === "/ads";

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 50);
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const scrollToForm = () => {
        const form = document.getElementById("form-contatto");
        if (form) {
            form.scrollIntoView({ behavior: "smooth" });
        } else {
            window.location.href = "/#form-contatto";
        }
        setMobileMenuOpen(false);
    };

    const scrollTo = (id: string) => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth" });
        setMobileMenuOpen(false);
    };

    const isAi = variant === "ai";

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                    ? "bg-[#0a0a1a]/90 backdrop-blur-xl border-b border-white/5 shadow-lg py-3"
                    : "bg-transparent py-5"
                }`}
        >
            <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
                <Link href="/" className="flex items-center">
                    <div className="relative h-10 w-40">
                        <Image
                            src="/logo.png"
                            alt="E-quipe"
                            fill
                            className="object-contain object-left"
                            priority
                        />
                    </div>
                </Link>

                {/* Pill toggle - 3 options */}
                <div className="hidden lg:flex items-center gap-1 bg-white/5 rounded-full p-1 border border-white/10">
                    <Link href="/" className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${!isOnAiPage && !isOnAdsPage ? "bg-[#0090FF] text-white shadow-md" : "text-gray-300 hover:text-white hover:bg-white/10"}`}>
                        {nav.customSite}
                    </Link>
                    <Link href="/ai-website-builder" className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${isOnAiPage ? "bg-[#7C3AED] text-white shadow-md" : "text-gray-300 hover:text-white hover:bg-white/10"}`}>
                        {nav.createWithAi}
                    </Link>
                    <Link href="/ads" className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${isOnAdsPage ? "bg-[#22C55E] text-white shadow-md" : "text-gray-300 hover:text-white hover:bg-white/10"}`}>
                        {nav.ads}
                    </Link>
                </div>

                {/* Right-side CTA + Language Switcher */}
                <div className="hidden lg:flex items-center gap-3">
                    <LanguageSwitcher />
                    {isAi ? (
                        <Link
                            href="/auth"
                            className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-lg font-bold text-sm transition-all shadow-lg shadow-purple-500/25 hover:-translate-y-0.5"
                        >
                            {nav.createFree}
                        </Link>
                    ) : (
                        <button
                            onClick={scrollToForm}
                            className={`px-6 py-2.5 text-white rounded-lg font-bold text-sm transition-all shadow-lg hover:-translate-y-0.5 ${isOnAdsPage ? "bg-[#22C55E] hover:bg-[#16A34A]" : "bg-[#0090FF] hover:bg-[#0070C9]"}`}
                        >
                            {nav.contact}
                        </button>
                    )}
                </div>

                {/* Mobile Menu Button */}
                <button
                    className="lg:hidden p-2 text-white"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                    {mobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="lg:hidden bg-[#0a0a1a] border-b border-white/10 overflow-hidden"
                    >
                        <div className="px-6 py-8 space-y-6 flex flex-col items-center">
                            {/* Language Switcher mobile */}
                            <LanguageSwitcher />

                            {/* Page toggle - 3 options */}
                            <div className="flex w-full gap-1 bg-white/5 rounded-full p-1 border border-white/10">
                                <Link href="/" onClick={() => setMobileMenuOpen(false)} className={`flex-1 py-2.5 rounded-full text-xs font-bold text-center transition-all ${!isOnAiPage && !isOnAdsPage ? "bg-[#0090FF] text-white" : "text-gray-300"}`}>
                                    {nav.customSite}
                                </Link>
                                <Link href="/ai-website-builder" onClick={() => setMobileMenuOpen(false)} className={`flex-1 py-2.5 rounded-full text-xs font-bold text-center transition-all ${isOnAiPage ? "bg-[#7C3AED] text-white" : "text-gray-300"}`}>
                                    {nav.createWithAi}
                                </Link>
                                <Link href="/ads" onClick={() => setMobileMenuOpen(false)} className={`flex-1 py-2.5 rounded-full text-xs font-bold text-center transition-all ${isOnAdsPage ? "bg-[#22C55E] text-white" : "text-gray-300"}`}>
                                    Ads
                                </Link>
                            </div>
                            <div className="w-full h-px bg-white/10" />
                            {isAi ? (
                                <>
                                    <button onClick={() => scrollTo("come-funziona")} className="text-lg text-gray-300 hover:text-white">{nav.howItWorks}</button>
                                    <button onClick={() => scrollTo("funzionalita")} className="text-lg text-gray-300 hover:text-white">{nav.features}</button>
                                    <button onClick={() => scrollTo("prezzi-ai")} className="text-lg text-gray-300 hover:text-white">{nav.pricing}</button>
                                    <button onClick={() => scrollTo("faq-ai")} className="text-lg text-gray-300 hover:text-white">{nav.faq}</button>
                                    <Link
                                        href="/auth"
                                        onClick={() => setMobileMenuOpen(false)}
                                        className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-bold text-lg text-center"
                                    >
                                        {nav.createFree}
                                    </Link>
                                </>
                            ) : (
                                <>
                                    <a href="/#portfolio" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">{nav.portfolio}</a>
                                    <a href="/#faq" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">{nav.faq}</a>
                                    <button
                                        onClick={scrollToForm}
                                        className={`w-full py-4 text-white rounded-xl font-bold text-lg ${isOnAdsPage ? "bg-[#22C55E]" : "bg-[#0090FF]"}`}
                                    >
                                        {nav.contact}
                                    </button>
                                </>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
}
