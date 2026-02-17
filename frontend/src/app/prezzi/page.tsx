"use client";

import Navbar from "@/components/layout/Navbar";
import Pricing from "@/components/sections/Pricing";
import ServicesList from "@/components/sections/ServicesList";
import Footer from "@/components/sections/Footer";

export default function PrezziPage() {
  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white overflow-x-hidden font-sans">
      <Navbar />
      <main className="pt-20">
        <Pricing />
        <ServicesList />
      </main>
      <Footer />
    </div>
  );
}
