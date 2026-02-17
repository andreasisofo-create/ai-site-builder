"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { useLanguage, translations } from "@/lib/i18n";

const images = [
    "/images/demos/professionalforce.png",
    "/images/demos/restinone.png",
    "/images/demos/fondazione.png",
    "/images/demos/nownow.png",
    "/images/demos/rallyroma.png",
    "/images/demos/maxrendina.png",
];

const urls = [
    "https://www.professionalforce.it/",
    "https://www.restinone.com/",
    "https://www.fondazioneitalianasport.it/",
    "https://www.now-now.it/",
    "https://www.rallydiromacapitale.it/",
    "https://www.maxrendina.it/",
];

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
};

export default function Portfolio() {
    const { language } = useLanguage();
    const txt = translations[language].portfolio;

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
                    <h2 className="text-3xl lg:text-5xl font-bold text-white mb-4">{txt.title}</h2>
                    <p className="text-xl text-gray-400">{txt.subtitle}</p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
                    {txt.items.map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial="hidden"
                            whileInView="visible"
                            viewport={{ once: true, margin: "-50px" }}
                            variants={fadeUp}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="group relative rounded-xl overflow-hidden bg-[#16162a] border border-white/5 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
                        >
                            {/* Image Container with Aspect Ratio */}
                            <div className="relative aspect-[16/9] w-full overflow-hidden bg-gray-800">
                                <Image
                                    src={images[idx]}
                                    alt={`${item.name} website`}
                                    fill
                                    className="object-cover object-top transition-transform duration-700 group-hover:scale-105"
                                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                                />
                                {/* Overlay on Hover */}
                                <div className="absolute inset-0 bg-[#0090FF]/90 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-sm">
                                    <Link
                                        href={urls[idx]}
                                        target="_blank"
                                        className="px-6 py-3 bg-white text-[#0090FF] rounded-full font-bold text-sm hover:bg-gray-100 transition-colors flex items-center gap-2 transform translate-y-4 group-hover:translate-y-0 duration-300"
                                    >
                                        {txt.visitSite} <ExternalLink className="w-4 h-4" />
                                    </Link>
                                </div>
                            </div>

                            {/* Content Below Image */}
                            <div className="p-6">
                                <h3 className="text-white font-bold text-lg mb-1">{item.name}</h3>
                                <p className="text-[#0090FF] text-sm font-medium">{item.sector}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
