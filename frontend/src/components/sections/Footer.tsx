"use client";

import Link from "next/link";
import Image from "next/image";
import { useLanguage, translations } from "@/lib/i18n";

export default function Footer() {
    const { language } = useLanguage();
    const txt = translations[language].footer;

    return (
        <footer className="bg-[#050510] pt-20 pb-10 border-t border-white/5">
            <div className="container mx-auto px-6">

                {/* Distinction Note */}
                <div className="mb-12 p-6 bg-[#0a0a1a] border border-white/5 rounded-xl text-center max-w-3xl mx-auto">
                    <h4 className="text-white font-bold mb-2">{txt.chooseYourPath}</h4>
                    <p className="text-gray-400 text-sm">
                        {language === "it" ? (
                            <>Offriamo due soluzioni distinte: <Link href="/" className="text-[#0090FF] hover:underline">{txt.customSite}</Link> (sviluppato dai nostri esperti) oppure <Link href="/ai-website-builder" className="text-[#0090FF] hover:underline">{txt.aiTechnology}</Link> (fai-da-te in autonomia). I prezzi e i servizi sono specifici per ogni soluzione.</>
                        ) : (
                            <>We offer two distinct solutions: <Link href="/" className="text-[#0090FF] hover:underline">{txt.customSite}</Link> (built by our experts) or <Link href="/ai-website-builder" className="text-[#0090FF] hover:underline">{txt.aiTechnology}</Link> (do-it-yourself). Pricing and services are specific to each solution.</>
                        )}
                    </p>
                </div>

                <div className="grid md:grid-cols-4 gap-12 mb-16">
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="inline-block mb-6 relative w-32 h-8">
                            <Image
                                src="/logo.png"
                                alt="E-quipe"
                                fill
                                className="object-contain object-left opacity-90"
                            />
                        </Link>
                        <p className="text-gray-400 text-sm leading-relaxed">
                            {txt.description}
                            <br /><br />
                            {txt.internalDoc}
                        </p>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">{txt.product}</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><Link href="/ai-website-builder" className="hover:text-[#0090FF] transition-colors">{txt.aiBuilder}</Link></li>
                            <li><a href="/#portfolio" className="hover:text-[#0090FF] transition-colors">{txt.agencyPortfolio}</a></li>
                            <li><a href="/#prezzi" className="hover:text-[#0090FF] transition-colors">{txt.agencyPricing}</a></li>
                            <li><Link href="/auth" className="hover:text-[#0090FF] transition-colors">Login</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">{txt.company}</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-[#0090FF] transition-colors">{txt.companyLinks.about}</a></li>
                            <li><a href="/#form-contatto" className="hover:text-[#0090FF] transition-colors">{txt.companyLinks.contact}</a></li>
                            <li><a href="#" className="hover:text-[#0090FF] transition-colors">{txt.companyLinks.blog}</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">{txt.legal}</h4>
                        <ul className="space-y-4 text-sm text-gray-400">
                            <li><a href="#" className="hover:text-[#0090FF] transition-colors">{txt.legalLinks.privacy}</a></li>
                            <li><a href="#" className="hover:text-[#0090FF] transition-colors">{txt.legalLinks.terms}</a></li>
                            <li><a href="#" className="hover:text-[#0090FF] transition-colors">{txt.legalLinks.cookies}</a></li>
                        </ul>
                    </div>
                </div>

                <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-center md:text-left text-gray-500">
                    <p>{txt.copyright}</p>
                </div>
            </div>
        </footer>
    );
}
