"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const items = [
    { name: "Ristorante Amore", sector: "Ristorante", image: "/images/demos/ristorante.webp" },
    { name: "Modern Hair Studio", sector: "Parrucchiere", image: "/images/demos/parrucchiere.webp" },
    { name: "Smile & Co. Dental", sector: "Studio Dentistico", image: "/images/demos/dentista.webp" },
    { name: "FitZone Gym", sector: "Palestra", image: "/images/demos/palestra.webp" },
    { name: "Studio Legale Rossi", sector: "Studio Professionale", image: "/images/demos/avvocato.webp" },
    { name: "Noir & Blanc", sector: "E-commerce", image: "/images/demos/ecommerce.webp" },
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
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">Loro l'hanno già fatto</h2>
                    <p className="text-xl text-gray-400">Attività reali che sono andate online con E-quipe.</p>
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
                            className="group relative rounded-xl overflow-hidden aspect-[4/3] bg-gray-800"
                        >
                            {/* Fallback color/placeholder since images might not exist locally yet */}
                            <div className="absolute inset-0 bg-gradient-to-br from-gray-700 to-gray-900 group-hover:scale-105 transition-transform duration-500" />

                            {/* Note: In a real scenario, use simple divs if images are missing */}
                            <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                                <span className="text-xs">[Image: {item.name}]</span>
                            </div>

                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center p-4 text-center">
                                <h3 className="text-white font-bold text-lg translate-y-4 group-hover:translate-y-0 transition-transform duration-300">{item.name}</h3>
                                <span className="text-sm text-gray-300 translate-y-4 group-hover:translate-y-0 transition-transform duration-300 delay-75">{item.sector}</span>
                                <span className="mt-4 text-[#FF6B35] text-sm font-semibold translate-y-4 group-hover:translate-y-0 transition-transform duration-300 delay-100">Vedi il sito →</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
