"use client";

import { motion } from "framer-motion";

const services = [
    {
        category: "Sito Web",
        items: [
            { name: "Homepage AI", price: "€299", note: "Una tantum" },
            { name: "Sito Web Custom (8 pag)", price: "€999", note: "Una tantum" },
            { name: "Pagina Extra", price: "€100", note: "cad." },
            { name: "Dominio .it/.com", price: "€59", note: "/anno" },
            { name: "Manutenzione & Hosting", price: "€39", note: "/mese" },
        ]
    },
    {
        category: "Ads Management",
        items: [
            { name: "Meta Ads", price: "€149", note: "/mese" },
            { name: "Meta Ads Pro", price: "€249", note: "/mese" },
            { name: "Google Ads", price: "€199", note: "/mese" },
            { name: "Full Ads (Meta + Google)", price: "€349", note: "/mese" },
        ]
    },
    {
        category: "Contenuti AI (Add-on)",
        items: [
            { name: "Contenuti Base (8/mese)", price: "€79", note: "/mese" },
            { name: "Contenuti Pro (Illimitati)", price: "€149", note: "/mese" },
        ]
    }
];

const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

export default function ServicesList() {
    return (
        <section className="py-20 bg-[#0f0f23] border-t border-white/5">
            <div className="container mx-auto px-6 max-w-5xl">
                <motion.div
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    variants={fadeUp}
                    className="text-center mb-12"
                >
                    <h2 className="text-2xl font-bold text-white mb-2">Listino Servizi a la Carte</h2>
                    <p className="text-gray-400">Componi la tua soluzione scegliendo i singoli servizi.</p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {services.map((cat, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true }}
                            variants={fadeUp}
                            transition={{ delay: idx * 0.1 }}
                        >
                            <h3 className="text-[#0090FF] font-bold uppercase tracking-wider text-sm mb-4 border-b border-[#0090FF]/20 pb-2">
                                {cat.category}
                            </h3>
                            <ul className="space-y-4">
                                {cat.items.map((item, i) => (
                                    <li key={i} className="flex justify-between items-start text-sm">
                                        <span className="text-gray-300 font-medium">{item.name}</span>
                                        <div className="text-right">
                                            <span className="block text-white font-bold">{item.price}</span>
                                            {item.note && <span className="text-gray-500 text-xs">{item.note}</span>}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
