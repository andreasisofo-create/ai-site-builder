"use client";

import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import MainHero from "@/components/sections/MainHero";
import SocialProof from "@/components/sections/SocialProof";
import HowItWorks from "@/components/sections/HowItWorks";
import Portfolio from "@/components/sections/Portfolio";
import ContactForm from "@/components/sections/ContactForm";
import Features from "@/components/sections/Features";
import AiBuilderSection from "@/components/sections/AiBuilderSection";
import Pricing from "@/components/sections/Pricing";
import ServicesList from "@/components/sections/ServicesList";
import AdsUpsell from "@/components/sections/AdsUpsell";
import Faq from "@/components/sections/Faq";
import FinalCta from "@/components/sections/FinalCta";
import Footer from "@/components/sections/Footer";

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isFormVisible, setIsFormVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsFormVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    const formElement = document.getElementById("form-contatto");
    if (formElement) {
      observer.observe(formElement);
    }

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (formElement) observer.unobserve(formElement);
    };
  }, []);

  const scrollToForm = () => {
    document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden font-sans">
      {/* ===== NAVBAR ===== */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
            ? "bg-[#0a0a1a]/90 backdrop-blur-xl border-b border-white/5 shadow-lg py-3"
            : "bg-transparent py-5"
          }`}
      >
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            {/* Logo Image */}
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

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-8">
            <a href="#come-funziona" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Come Funziona</a>
            <a href="#portfolio" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Portfolio</a>
            <a href="#prezzi" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Prezzi</a>
            <a href="#faq" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">FAQ</a>
          </div>

          <div className="hidden lg:flex items-center gap-4">
            {/* CTA - BLUE */}
            <button
              onClick={scrollToForm}
              className="px-6 py-2.5 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-lg font-bold text-sm transition-all shadow-lg hover:-translate-y-0.5"
            >
              Contattaci
            </button>
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
                <a href="#come-funziona" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">Come Funziona</a>
                <a href="#portfolio" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">Portfolio</a>
                <a href="#prezzi" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">Prezzi</a>
                <a href="#faq" onClick={() => setMobileMenuOpen(false)} className="text-lg text-gray-300 hover:text-white">FAQ</a>
                <button
                  onClick={scrollToForm}
                  className="w-full py-4 bg-[#0090FF] text-white rounded-xl font-bold text-lg"
                >
                  Contattaci
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Sticky Mobile Bottom Bar */}
      {!isFormVisible && (
        <div className="lg:hidden fixed bottom-6 left-6 right-6 z-40 pointer-events-none">
          <button
            onClick={scrollToForm}
            className="w-full py-4 bg-[#0090FF] text-white rounded-xl font-bold text-lg shadow-2xl pointer-events-auto shadow-blue-900/40 border border-white/10 backdrop-blur-md"
          >
            Contattaci — è gratis
          </button>
        </div>
      )}

      <main>
        <MainHero />
        <SocialProof />
        <HowItWorks />
        <Portfolio />
        <ContactForm />
        <Features />
        <Pricing />
        <ServicesList />
        <AiBuilderSection />
        <AdsUpsell />
        <Faq />
        <FinalCta />
      </main>

      <Footer />
    </div>
  );
}
