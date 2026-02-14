"use client";

import { useLanguage } from "@/lib/i18n";

interface LanguageSwitcherProps {
  variant?: "dark" | "light";
}

export default function LanguageSwitcher({ variant = "dark" }: LanguageSwitcherProps) {
  const { language, setLanguage } = useLanguage();

  const isLight = variant === "light";

  return (
    <div
      className={`flex items-center rounded-full p-0.5 text-xs font-medium ${
        isLight
          ? "bg-slate-100 border border-slate-200"
          : "bg-white/5 border border-white/10"
      }`}
    >
      <button
        onClick={() => setLanguage("it")}
        className={`px-2.5 py-1 rounded-full transition-all duration-200 ${
          language === "it"
            ? isLight
              ? "bg-white text-slate-900 shadow-sm"
              : "bg-white/15 text-white"
            : isLight
              ? "text-slate-500 hover:text-slate-700"
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
            ? isLight
              ? "bg-white text-slate-900 shadow-sm"
              : "bg-white/15 text-white"
            : isLight
              ? "text-slate-500 hover:text-slate-700"
              : "text-slate-400 hover:text-slate-200"
        }`}
        aria-label="English"
      >
        EN
      </button>
    </div>
  );
}
