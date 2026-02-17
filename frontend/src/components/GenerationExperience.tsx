"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import {
  SparklesIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  CubeIcon,
  CheckIcon,
  PhotoIcon,
} from "@heroicons/react/24/outline";
import { useLanguage } from "@/lib/i18n";

// Preview data structure from the backend
export interface PreviewData {
  phase: "analyzing" | "theme_complete" | "content_complete" | "assembled" | "complete";
  colors?: {
    primary: string;
    secondary: string;
    accent: string;
    bg: string;
    text: string;
  };
  font_heading?: string;
  font_body?: string;
  sections?: string[];
  hero_title?: string;
  hero_subtitle?: string;
  hero_cta?: string;
  services_titles?: string[];
}

interface GenerationExperienceProps {
  step: number;
  totalSteps: number;
  message: string;
  percentage: number;
  previewData: PreviewData | null;
}

const STEP_CONFIG = {
  it: [
    { icon: SparklesIcon, label: "Analisi stile e testi", color: "blue" },
    { icon: PaintBrushIcon, label: "Palette e componenti", color: "violet" },
    { icon: DocumentTextIcon, label: "Contenuti e layout", color: "emerald" },
    { icon: PhotoIcon, label: "Generazione immagini", color: "pink" },
    { icon: CubeIcon, label: "Assemblaggio finale", color: "amber" },
  ],
  en: [
    { icon: SparklesIcon, label: "Style & text analysis", color: "blue" },
    { icon: PaintBrushIcon, label: "Palette & components", color: "violet" },
    { icon: DocumentTextIcon, label: "Content & layout", color: "emerald" },
    { icon: PhotoIcon, label: "Image generation", color: "pink" },
    { icon: CubeIcon, label: "Final assembly", color: "amber" },
  ],
};

const UI_TEXT = {
  it: {
    stepLabel: "Step",
    processing: "Elaborazione...",
    analyzing: "L'AI sta analizzando il tuo business e creando contenuti unici...",
    paletteTitle: "Palette colori selezionata",
    fontHeading: "Font titoli",
    fontBody: "Font corpo",
    contentPreview: "Anteprima contenuti",
    assembling: "Assemblaggio del sito in corso...",
    siteReady: "Il tuo sito e' pronto!",
    redirecting: "Reindirizzamento all'editor...",
  },
  en: {
    stepLabel: "Step",
    processing: "Processing...",
    analyzing: "AI is analyzing your business and creating unique content...",
    paletteTitle: "Selected color palette",
    fontHeading: "Heading font",
    fontBody: "Body font",
    contentPreview: "Content preview",
    assembling: "Assembling your site...",
    siteReady: "Your site is ready!",
    redirecting: "Redirecting to editor...",
  },
};

// Skeleton section shapes for analyzing phase
const SKELETON_SECTIONS = [
  { h: "h-32", span: "col-span-full" },       // hero
  { h: "h-16", span: "col-span-1" },           // section
  { h: "h-16", span: "col-span-1" },           // section
  { h: "h-20", span: "col-span-full" },        // wide section
  { h: "h-14", span: "col-span-1" },           // section
  { h: "h-14", span: "col-span-1" },           // section
];

// Typewriter hook
function useTypewriter(text: string, speed = 40) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const indexRef = useRef(0);

  useEffect(() => {
    if (!text) { setDisplayed(""); setDone(false); return; }
    setDisplayed("");
    setDone(false);
    indexRef.current = 0;

    const interval = setInterval(() => {
      indexRef.current++;
      if (indexRef.current >= text.length) {
        setDisplayed(text);
        setDone(true);
        clearInterval(interval);
      } else {
        setDisplayed(text.slice(0, indexRef.current));
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return { displayed, done };
}

export default function GenerationExperience({
  step,
  totalSteps,
  message,
  percentage,
  previewData,
}: GenerationExperienceProps) {
  const { language } = useLanguage();
  const lang = language as "it" | "en";
  const text = UI_TEXT[lang];
  const steps = STEP_CONFIG[lang];

  const [animatedPercentage, setAnimatedPercentage] = useState(0);
  const [showContent, setShowContent] = useState(false);
  const [fontLoaded, setFontLoaded] = useState(false);
  const [colorRevealIndex, setColorRevealIndex] = useState(0);

  // Smooth percentage animation
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercentage(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  // Content reveal delay
  useEffect(() => {
    if (previewData) {
      const timer = setTimeout(() => setShowContent(true), 300);
      return () => clearTimeout(timer);
    }
    setShowContent(false);
  }, [previewData?.phase]);

  // Staggered color reveal for theme_complete phase
  useEffect(() => {
    if (previewData?.phase === "theme_complete" && previewData.colors) {
      setColorRevealIndex(0);
      const count = Object.keys(previewData.colors).length;
      let i = 0;
      const interval = setInterval(() => {
        i++;
        setColorRevealIndex(i);
        if (i >= count) clearInterval(interval);
      }, 150);
      return () => clearInterval(interval);
    }
  }, [previewData?.phase]);

  // Load Google Font for preview
  const loadFont = useCallback((fontName: string) => {
    if (!fontName || typeof document === "undefined") return;
    const id = `gen-font-${fontName.replace(/\s+/g, "-")}`;
    if (document.getElementById(id)) { setFontLoaded(true); return; }
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontName)}:wght@400;700&display=swap`;
    link.onload = () => setFontLoaded(true);
    document.head.appendChild(link);
  }, []);

  useEffect(() => {
    if (previewData?.font_heading) {
      setFontLoaded(false);
      loadFont(previewData.font_heading);
    }
    if (previewData?.font_body) {
      loadFont(previewData.font_body);
    }
  }, [previewData?.font_heading, previewData?.font_body, loadFont]);

  // Typewriter for hero title in content_complete phase
  const heroTitle = previewData?.phase === "content_complete" ? (previewData?.hero_title || "") : "";
  const { displayed: typedTitle, done: titleDone } = useTypewriter(heroTitle);

  const phase = previewData?.phase || "analyzing";

  return (
    <div className="w-full space-y-8">
      {/* Main Progress Circle */}
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60" cy="60" r="52"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="8"
            />
            <circle
              cx="60" cy="60" r="52"
              fill="none"
              stroke="url(#progressGradient)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 52}`}
              strokeDashoffset={`${2 * Math.PI * 52 * (1 - animatedPercentage / 100)}`}
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold">{Math.round(animatedPercentage)}%</span>
            <span className="text-xs text-slate-500">{text.stepLabel} {step}/{totalSteps}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-300">
          <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
          <span className="text-sm">{message || text.processing}</span>
        </div>
      </div>

      {/* Step indicators */}
      <div className="grid grid-cols-5 gap-2">
        {steps.map((cfg, idx) => {
          const stepNum = idx + 1;
          const Icon = cfg.icon;
          const isActive = step === stepNum;
          const isDone = step > stepNum;

          return (
            <div
              key={stepNum}
              className={`flex flex-col items-center gap-2 p-3 rounded-xl text-xs transition-all duration-500 ${
                isActive
                  ? "bg-blue-500/10 border border-blue-500/30 text-blue-400"
                  : isDone
                  ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                  : "bg-white/[0.02] border border-white/5 text-slate-600"
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                isActive
                  ? "bg-blue-500/20"
                  : isDone
                  ? "bg-emerald-500/20"
                  : "bg-white/5"
              }`}>
                {isDone ? (
                  <CheckIcon className="w-4 h-4" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span className="text-center leading-tight">{cfg.label}</span>
            </div>
          );
        })}
      </div>

      {/* Progressive Preview Scenes */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">

        {/* Scene 1: Analyzing — skeleton placeholders */}
        {phase === "analyzing" && (
          <div className="p-6 space-y-4 animate-in fade-in duration-500">
            <div className="flex items-center gap-3 mb-2">
              <div className="relative">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 animate-pulse" />
                <SparklesIcon className="w-5 h-5 text-blue-400 absolute inset-0 m-auto" />
              </div>
              <p className="text-sm text-slate-400">{text.analyzing}</p>
            </div>
            {/* Skeleton site wireframe */}
            <div className="grid grid-cols-2 gap-2">
              {SKELETON_SECTIONS.map((sec, i) => (
                <div
                  key={i}
                  className={`${sec.h} ${sec.span} rounded-lg overflow-hidden relative border border-white/[0.06]`}
                >
                  <div
                    className="absolute inset-0 bg-gradient-to-r from-white/[0.03] via-white/[0.12] to-white/[0.03]"
                    style={{
                      animation: `shimmer 1.2s linear infinite`,
                      animationDelay: `${i * 0.15}s`,
                      backgroundSize: "200% 100%",
                    }}
                  />
                </div>
              ))}
            </div>
            {/* Font name placeholder skeletons */}
            <div className="flex items-center gap-4 mt-3">
              <div className="h-3 w-28 rounded bg-white/[0.04] overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-r from-white/[0.03] via-white/[0.12] to-white/[0.03]" style={{ animation: "shimmer 1.2s linear infinite", backgroundSize: "200% 100%" }} />
              </div>
              <div className="h-3 w-20 rounded bg-white/[0.04] overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-r from-white/[0.03] via-white/[0.12] to-white/[0.03]" style={{ animation: "shimmer 1.2s linear infinite", animationDelay: "0.3s", backgroundSize: "200% 100%" }} />
              </div>
            </div>
            <style>{`
              @keyframes shimmer {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
              }
            `}</style>
          </div>
        )}

        {/* Scene 2: Theme complete — palette, fonts, mini-mockup */}
        {phase === "theme_complete" && previewData?.colors && (
          <div className={`p-6 space-y-5 transition-all duration-700 ${showContent ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <PaintBrushIcon className="w-4 h-4 text-violet-400" />
              {text.paletteTitle}
            </h4>
            {/* Color circles with staggered reveal */}
            <div className="flex gap-3">
              {Object.entries(previewData.colors).map(([name, hex], idx) => (
                <div
                  key={name}
                  className="flex flex-col items-center gap-1.5 transition-all duration-500"
                  style={{
                    opacity: idx < colorRevealIndex ? 1 : 0,
                    transform: idx < colorRevealIndex ? "scale(1)" : "scale(0.5)",
                  }}
                >
                  <div
                    className="w-12 h-12 rounded-xl shadow-lg transition-transform hover:scale-110"
                    style={{ backgroundColor: hex }}
                  />
                  <span className="text-[10px] text-slate-500 capitalize">{name}</span>
                </div>
              ))}
            </div>
            {/* Font preview with actual Google Font */}
            {previewData.font_heading && (
              <div className="pt-3 border-t border-white/5 space-y-2">
                <div className="flex items-baseline gap-4">
                  <div className="text-xs text-slate-500">
                    {text.fontHeading}:
                  </div>
                  <span
                    className="text-lg text-slate-200 transition-opacity duration-500"
                    style={{
                      fontFamily: fontLoaded ? `'${previewData.font_heading}', sans-serif` : "sans-serif",
                      opacity: fontLoaded ? 1 : 0.4,
                    }}
                  >
                    {previewData.font_heading}
                  </span>
                </div>
                {previewData.font_body && (
                  <div className="flex items-baseline gap-4">
                    <div className="text-xs text-slate-500">
                      {text.fontBody}:
                    </div>
                    <span
                      className="text-sm text-slate-400 transition-opacity duration-500"
                      style={{
                        fontFamily: fontLoaded ? `'${previewData.font_body}', sans-serif` : "sans-serif",
                        opacity: fontLoaded ? 1 : 0.4,
                      }}
                    >
                      {previewData.font_body}
                    </span>
                  </div>
                )}
              </div>
            )}
            {/* Mini gradient mockup with chosen colors */}
            <div
              className="h-16 rounded-xl border border-white/5 transition-all duration-1000"
              style={{
                background: `linear-gradient(135deg, ${previewData.colors.primary}20, ${previewData.colors.secondary}20, ${previewData.colors.accent}20)`,
              }}
            />
          </div>
        )}

        {/* Scene 3: Content complete — typewriter hero + services + sections */}
        {phase === "content_complete" && (
          <div className={`transition-all duration-700 ${showContent ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <div className="p-6 space-y-4">
              <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <DocumentTextIcon className="w-4 h-4 text-emerald-400" />
                {text.contentPreview}
              </h4>

              {/* Hero preview with typewriter effect */}
              {previewData?.hero_title && (
                <div
                  className="p-4 rounded-xl border border-white/10"
                  style={{
                    background: previewData?.colors
                      ? `linear-gradient(135deg, ${previewData.colors.primary}15, ${previewData.colors.secondary}15)`
                      : "rgba(255,255,255,0.02)",
                  }}
                >
                  <p
                    className="text-lg font-bold mb-1"
                    style={{
                      color: previewData?.colors?.primary || "#3b82f6",
                      fontFamily: previewData?.font_heading ? `'${previewData.font_heading}', sans-serif` : undefined,
                    }}
                  >
                    {typedTitle}
                    {!titleDone && <span className="animate-pulse">|</span>}
                  </p>
                  {/* Subtitle appears after typewriter finishes */}
                  {previewData.hero_subtitle && (
                    <p
                      className="text-sm text-slate-400 mb-2 transition-all duration-500"
                      style={{
                        opacity: titleDone ? 1 : 0,
                        transform: titleDone ? "translateY(0)" : "translateY(8px)",
                        fontFamily: previewData?.font_body ? `'${previewData.font_body}', sans-serif` : undefined,
                      }}
                    >
                      {previewData.hero_subtitle}
                    </p>
                  )}
                  {/* CTA button scales in after subtitle */}
                  {previewData.hero_cta && (
                    <span
                      className="inline-block px-3 py-1 rounded-lg text-xs text-white transition-all duration-500"
                      style={{
                        backgroundColor: previewData?.colors?.primary || "#3b82f6",
                        opacity: titleDone ? 1 : 0,
                        transform: titleDone ? "scale(1)" : "scale(0.8)",
                      }}
                    >
                      {previewData.hero_cta}
                    </span>
                  )}
                </div>
              )}

              {/* Services preview with stagger */}
              {previewData?.services_titles && previewData.services_titles.length > 0 && (
                <div className="grid grid-cols-3 gap-2">
                  {previewData.services_titles.slice(0, 3).map((title, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-white/[0.03] border border-white/5 text-center transition-all duration-500"
                      style={{
                        animationDelay: `${i * 0.12}s`,
                        opacity: titleDone ? 1 : 0,
                        transform: titleDone ? "translateY(0)" : "translateY(12px)",
                        transitionDelay: `${i * 120}ms`,
                      }}
                    >
                      <p className="text-xs text-slate-300 truncate">{title}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Section badges with stagger */}
              {previewData?.sections && (
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {previewData.sections.map((s, i) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded-full bg-white/5 text-[10px] text-slate-500 capitalize transition-all duration-300"
                      style={{
                        opacity: titleDone ? 1 : 0,
                        transform: titleDone ? "scale(1)" : "scale(0.7)",
                        transitionDelay: `${i * 80}ms`,
                      }}
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scene 4: Assembled — mini wireframe with section blocks */}
        {phase === "assembled" && previewData?.sections && (
          <div className={`p-6 space-y-3 transition-all duration-700 ${showContent ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <CubeIcon className="w-4 h-4 text-amber-400" />
              {text.assembling}
            </h4>
            <div className="space-y-1.5">
              {previewData.sections.map((section, i) => (
                <div
                  key={section}
                  className="rounded-lg border border-white/5 px-3 py-2 flex items-center gap-2 transition-all duration-500"
                  style={{
                    background: previewData?.colors
                      ? `linear-gradient(90deg, ${previewData.colors.primary}08, transparent)`
                      : "rgba(255,255,255,0.02)",
                    opacity: showContent ? 1 : 0,
                    transform: showContent ? "translateX(0)" : "translateX(-12px)",
                    transitionDelay: `${i * 100}ms`,
                  }}
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: previewData?.colors?.primary || "#3b82f6" }}
                  />
                  <span className="text-xs text-slate-400 capitalize">{section}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scene 5: Complete */}
        {phase === "complete" && (
          <div className="p-8 flex flex-col items-center gap-3 animate-in fade-in duration-500">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <CheckIcon className="w-8 h-8 text-emerald-400" />
            </div>
            <p className="text-sm font-medium text-emerald-400">{text.siteReady}</p>
            <p className="text-xs text-slate-500">{text.redirecting}</p>
          </div>
        )}
      </div>
    </div>
  );
}
