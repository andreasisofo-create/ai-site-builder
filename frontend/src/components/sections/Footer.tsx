"use client";

import Link from "next/link";
import Image from "next/image";

export default function Footer() {
    return (
        <footer className="bg-[#050510] pt-20 pb-10 border-t border-white/5">
            <div className="container mx-auto px-6">
                <div className="grid md:grid-cols-4 gap-12 mb-16">
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="inline-block mb-6">
                            <Image
                                src="/e-quipe-logo.png"
                                alt="E-quipe"
                                width={120}
                                height={34}
                                className="h-8 w-auto opacity-90"
                            />
                        </Link>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            E-quipe crea il tuo sito web con l'intelligenza artificiale e gestisce le campagne pubblicitarie per portarti clienti reali.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Prodotto</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><a href="#come-funziona" className="hover:text-[#FF6B35] transition-colors">Come Funziona</a></li>
                            <li><a href="#portfolio" className="hover:text-[#FF6B35] transition-colors">Portfolio</a></li>
                            <li><a href="#prezzi" className="hover:text-[#FF6B35] transition-colors">Prezzi</a></li>
                            <li><Link href="/auth" className="hover:text-[#FF6B35] transition-colors">App AI</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Azienda</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-[#FF6B35] transition-colors">Chi Siamo</a></li>
                            <li><a href="#form-contatto" className="hover:text-[#FF6B35] transition-colors">Contatti</a></li>
                            <li><a href="#" className="hover:text-[#FF6B35] transition-colors">Blog</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Legale</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-[#FF6B35] transition-colors">Privacy Policy</a></li>
                            <li><a href="#" className="hover:text-[#FF6B35] transition-colors">Termini di Servizio</a></li>
                            <li><a href="#" className="hover:text-[#FF6B35] transition-colors">Cookie Policy</a></li>
                        </ul>
                    </div>
                </div>

                <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-center md:text-left text-gray-500">
                    <p>© 2026 E-quipe S.r.l.s. Tutti i diritti riservati.</p>
                    <p>P.IVA: 00000000000</p>
                </div>
            </div>
        </footer>
    );
}
