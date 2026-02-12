"use client";

import { useLanguage } from "@/lib/i18n";

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center rounded-full bg-white/5 border border-white/10 p-0.5 text-xs font-medium">
      <button
        onClick={() => setLanguage("it")}
        className={`px-2.5 py-1 rounded-full transition-all duration-200 ${
          language === "it"
            ? "bg-white/15 text-white"
            : "text-slate-400 hover:text-slate-200"
        }`}
        aria-label="Italiano"
      >
        IT
      </button>
      <button
        onClick={() => setLanguage("en")}
        className={`px-2.5 py-1 rounded-full transition-all duration-200 ${
          language === "en"
            ? "bg-white/15 text-white"
            : "text-slate-400 hover:text-slate-200"
        }`}
        aria-label="English"
      >
        EN
      </button>
    </div>
  );
}
