"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqs = [
    {
        q: "Davvero il sito è gratis?",
        a: "Sì. Creiamo il tuo sito senza nessun costo. Lo vedi, lo provi. Se ti piace scegli un piano per metterlo online. Se non ti convince, non paghi nulla."
    },
    {
        q: "Devo saper programmare?",
        a: "Assolutamente no. Ci occupiamo di tutto noi. Tu ci racconti la tua attività, noi facciamo il resto."
    },
    {
        q: "Quanto ci mette a creare il sito?",
        a: "Il sito viene creato in pochi giorni lavorativi. Se usi l'app AI, in 60 secondi hai già una prima versione."
    },
    {
        q: "Posso usare il mio dominio (es. mionome.it)?",
        a: "Sì, con i piani Business e superiori puoi collegare il tuo dominio personalizzato."
    },
    {
        q: "Qual è la differenza tra il servizio su misura e l'app AI?",
        a: "Con il servizio su misura, il nostro team crea tutto per te. Con l'app AI, fai tu in autonomia. In entrambi i casi, il risultato è un sito professionale."
    },
    {
        q: "Come funzionano le campagne pubblicitarie?",
        a: "Il nostro team gestisce le campagne Meta e Google Ads. Tu scegli il budget, noi ottimizziamo i risultati."
    },
    {
        q: "Posso iniziare solo col sito e aggiungere le campagne dopo?",
        a: "Certo. Parti con il sito e quando vuoi crescere attivi il servizio Ads."
    },
    {
        q: "Posso disdire quando voglio?",
        a: "Sì, nessun vincolo. Puoi disdire il piano in qualsiasi momento."
    }
];

export default function Faq() {
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    return (
        <section id="faq" className="py-20 bg-[#0a0a1a]">
            <div className="container mx-auto px-6 max-w-4xl">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-white mb-4">Domande frequenti</h2>
                </div>

                <div className="space-y-4">
                    {faqs.map((faq, idx) => (
                        <div key={idx} className="bg-[#16162a] rounded-xl border border-white/5 overflow-hidden">
                            <button
                                onClick={() => setOpenIndex(active => active === idx ? null : idx)}
                                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                            >
                                <span className="font-semibold text-white">{faq.q}</span>
                                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openIndex === idx ? "rotate-180" : ""}`} />
                            </button>
                            <AnimatePresence>
                                {openIndex === idx && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                    >
                                        <div className="px-6 pb-4 pt-0 text-gray-400 text-sm leading-relaxed border-t border-white/5 pt-4">
                                            {faq.a}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
