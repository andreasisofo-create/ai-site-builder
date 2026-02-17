"use client";

import { useState, useEffect } from "react";
import { useLanguage, translations } from "@/lib/i18n";
import Navbar from "@/components/layout/Navbar";
import MainHero from "@/components/sections/MainHero";
import SocialProof from "@/components/sections/SocialProof";
import HowItWorks from "@/components/sections/HowItWorks";
import Portfolio from "@/components/sections/Portfolio";
import ContactForm from "@/components/sections/ContactForm";
import Features from "@/components/sections/Features";
import AiBuilderSection from "@/components/sections/AiBuilderSection";
import AdsUpsell from "@/components/sections/AdsUpsell";
import Faq from "@/components/sections/Faq";
import FinalCta from "@/components/sections/FinalCta";
import Footer from "@/components/sections/Footer";

export default function LandingPage() {
  const { language } = useLanguage();
  const txt = translations[language].page;
  const [isFormVisible, setIsFormVisible] = useState(false);

  useEffect(() => {
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
      if (formElement) observer.unobserve(formElement);
    };
  }, []);

  const scrollToForm = () => {
    document.getElementById("form-contatto")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden font-sans">
      <Navbar />

      {/* Sticky Mobile Bottom Bar */}
      {!isFormVisible && (
        <div className="lg:hidden fixed bottom-6 left-6 right-6 z-40 pointer-events-none">
          <button
            onClick={scrollToForm}
            className="w-full py-4 bg-[#0090FF] text-white rounded-xl font-bold text-lg shadow-2xl pointer-events-auto shadow-blue-900/40 border border-white/10 backdrop-blur-md"
          >
            {txt.mobileCta}
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
        {/* Pricing REMOVED from Home Agency page as requested */}
        {/* ServicesList REMOVED from Home Agency page as requested */}
        <AiBuilderSection />
        <AdsUpsell />
        <Faq />
        <FinalCta />
      </main>

      <Footer />
    </div>
  );
}
