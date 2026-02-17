"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/lib/auth-context";

const services = [
    {
        category: "Sito Web",
        items: [
            { name: "Homepage AI", slug: "homepage-ai", price: "\u20AC299", note: "Una tantum" },
            { name: "Sito Web Custom (8 pag)", slug: "sito-web-custom", price: "\u20AC999", note: "Una tantum" },
            { name: "Pagina Extra", slug: "pagina-extra", price: "\u20AC100", note: "cad." },
            { name: "Dominio .it/.com", slug: "dominio", price: "\u20AC59", note: "/anno" },
            { name: "Manutenzione & Hosting", slug: "manutenzione-hosting", price: "\u20AC39", note: "/mese" },
        ]
    },
    {
        category: "Ads Management",
        items: [
            { name: "Meta Ads", slug: "meta-ads", price: "\u20AC149", note: "/mese" },
            { name: "Meta Ads Pro", slug: "meta-ads-pro", price: "\u20AC249", note: "/mese" },
            { name: "Google Ads", slug: "google-ads", price: "\u20AC199", note: "/mese" },
            { name: "Full Ads (Meta + Google)", slug: "full-ads", price: "\u20AC349", note: "/mese" },
        ]
    },
    {
        category: "Contenuti AI (Add-on)",
        items: [
            { name: "Contenuti Base (8/mese)", slug: "contenuti-base", price: "\u20AC79", note: "/mese" },
            { name: "Contenuti Pro (Illimitati)", slug: "contenuti-pro", price: "\u20AC149", note: "/mese" },
        ]
    }
];

const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

export default function ServicesList() {
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
                                        <button
                                            onClick={() => handleCheckout(item.slug)}
                                            className="text-gray-300 font-medium hover:text-white transition-colors text-left flex items-center gap-2"
                                        >
                                            {item.name}
                                        </button>
                                        <div className="text-right flex-shrink-0 ml-4">
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
