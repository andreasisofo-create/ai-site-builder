"use client";

import { SparklesIcon } from "@heroicons/react/24/outline";
import { useLanguage } from "@/lib/i18n";

interface EquipePromoProps {
  /** User email to pre-fill in the mailto body */
  userEmail?: string;
  /** Site name to include in the mailto body */
  siteName?: string;
  /** Render as a compact inline card instead of the default floating bar */
  variant?: "bar" | "card";
}

export default function EquipePromo({
  userEmail,
  siteName,
  variant = "bar",
}: EquipePromoProps) {
  const { language } = useLanguage();
  const isEn = language === "en";

  const handleContact = () => {
    const lines = [
      isEn ? "Hello," : "Buongiorno,",
      "",
      isEn
        ? "I would like a professional website with advanced features."
        : "Vorrei un sito professionale con funzionalita avanzate.",
      "",
      siteName ? `${isEn ? "Reference site" : "Sito di riferimento"}: ${siteName}` : "",
      userEmail ? `${isEn ? "My account" : "Il mio account"}: ${userEmail}` : "",
      "",
      isEn ? "Thank you" : "Grazie",
    ]
      .filter(Boolean)
      .join("\n");

    window.location.href = `mailto:andrea.sisofo@e-quipe.it?subject=${encodeURIComponent(
      isEn
        ? "Professional website request - Site Builder"
        : "Richiesta sito professionale - Site Builder"
    )}&body=${encodeURIComponent(lines)}`;
  };

  const title = isEn
    ? "Want a professional site with advanced features?"
    : "Vuoi un sito professionale con funzionalita avanzate?";
  const subtitle = isEn
    ? "The e-quipe Studio team can create a custom site for your business"
    : "Il team di e-quipe Studio puo creare un sito su misura per la tua attivita";
  const ctaLabel = isEn ? "Contact e-quipe Studio" : "Contatta e-quipe Studio";

  if (variant === "card") {
    return (
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600/20 via-indigo-600/15 to-purple-600/20 border border-violet-500/20 p-6">
        <div className="absolute -top-12 -right-12 w-40 h-40 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-violet-500/20 flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-violet-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-sm leading-tight">
              {title}
            </h3>
            <p className="text-slate-400 text-xs mt-1 leading-relaxed">
              {subtitle}
            </p>
            <button
              onClick={handleContact}
              className="mt-3 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg bg-violet-600 hover:bg-violet-500 text-white transition-colors"
            >
              <SparklesIcon className="w-3.5 h-3.5" />
              {ctaLabel}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-600/15 via-indigo-600/10 to-purple-600/15 border border-violet-500/15 px-5 py-4">
      <div className="absolute -top-8 left-1/2 -translate-x-1/2 w-60 h-24 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-violet-500/20 flex items-center justify-center">
            <SparklesIcon className="w-4 h-4 text-violet-400" />
          </div>
          <div className="min-w-0">
            <p className="text-white text-sm font-medium truncate">
              {title}
            </p>
            <p className="text-slate-400 text-xs truncate">
              {subtitle}
            </p>
          </div>
        </div>
        <button
          onClick={handleContact}
          className="flex-shrink-0 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg bg-violet-600 hover:bg-violet-500 text-white transition-colors"
        >
          <SparklesIcon className="w-3.5 h-3.5" />
          {ctaLabel}
        </button>
      </div>
    </div>
  );
}
