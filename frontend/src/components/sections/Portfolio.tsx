"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const items = [
    { name: "Demo Ristorante", sector: "Ristorante", image: "/images/demos/ristorante.webp" },
    { name: "Demo Parrucchiere", sector: "Parrucchiere", image: "/images/demos/parrucchiere.webp" },
    { name: "Demo Dentista", sector: "Studio Dentistico", image: "/images/demos/dentista.webp" },
    { name: "Demo Palestra", sector: "Palestra", image: "/images/demos/palestra.webp" },
    { name: "Demo Avvocato", sector: "Studio Professionale", image: "/images/demos/avvocato.webp" },
    { name: "Demo E-commerce", sector: "E-commerce", image: "/images/demos/ecommerce.webp" },
];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Portfolio() {
    return (
        <section id="portfolio" className="py-20 lg:py-28 bg-[#0f0f23]">
            <div className="container mx-auto px-6">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Esempi di siti realizzati</h2>
                    <p className="text-xl text-gray-400">Guarda la qualità che possiamo offrire alla tua attività.</p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {items.map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true, margin: "-50px" }}
                            variants={fadeUp}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="group relative rounded-xl overflow-hidden aspect-[4/3] bg-gray-800 border border-white/5"
                        >
                            {/* Fallback color if image is missing */}
                            <div className="absolute inset-0 bg-gradient-to-br from-[#1a1a2e] to-[#0f0f23] group-hover:scale-105 transition-transform duration-500" />

                            {/* Try to load image if available, otherwise show placeholder text */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-bold text-white/10 group-hover:text-white/20 transition-colors uppercase tracking-widest">{item.sector}</span>
                            </div>

                            <div className="absolute inset-0 bg-[#0090FF]/80 mix-blend-multiply opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                            <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-4 group-hover:translate-y-0">
                                <h3 className="text-white font-bold text-lg mb-1">{item.name}</h3>
                                <span className="text-white/80 text-sm mb-4">{item.sector}</span>
                                <button className="px-6 py-2 bg-white text-[#0090FF] rounded-full font-bold text-sm hover:bg-gray-100 transition-colors">
                                    Vedi Anteprima
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
