"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  SparklesIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  PhotoIcon,
  CubeIcon,
  CheckIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";
import { getGenerationStatus } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

// ============ CODE SNIPPETS POOL ============

const CODE_SNIPPETS = [
  '<!DOCTYPE html>',
  '<html lang="it">',
  '<head>',
  '  <meta charset="UTF-8">',
  '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
  '  <title>{{SITE_TITLE}}</title>',
  '  <style>',
  '    :root {',
  '      --color-primary: #7C3AED;',
  '      --color-secondary: #1E40AF;',
  '      --color-accent: #F59E0B;',
  '      --color-bg: #FAF7F2;',
  '    }',
  '    * { margin: 0; padding: 0; box-sizing: border-box; }',
  '    body { font-family: "DM Sans", sans-serif; }',
  '  </style>',
  '</head>',
  '<body>',
  '',
  '<!-- Hero Section -->',
  '<section class="hero" data-animate="fade-up">',
  '  <div class="hero-container">',
  '    <h1 data-animate="text-split">',
  '      {{HERO_TITLE}}',
  '    </h1>',
  '    <p data-animate="fade-up" data-delay="0.3">',
  '      {{HERO_SUBTITLE}}',
  '    </p>',
  '    <a href="#contact" class="cta-btn" data-animate="magnetic">',
  '      {{CTA_TEXT}}',
  '    </a>',
  '  </div>',
  '  <div class="hero-image" data-animate="scale-in">',
  '    <img src="hero.webp" alt="Hero" />',
  '  </div>',
  '</section>',
  '',
  '<!-- Services Section -->',
  '<section class="services py-24" data-animate="fade-up">',
  '  <div class="max-w-7xl mx-auto px-6">',
  '    <h2 data-animate="text-split">{{SERVICES_TITLE}}</h2>',
  '    <div class="grid grid-cols-3 gap-8 mt-16">',
  '      <div class="service-card" data-animate="tilt">',
  '        <span class="icon">{{SERVICE_ICON}}</span>',
  '        <h3>{{SERVICE_TITLE}}</h3>',
  '        <p>{{SERVICE_DESCRIPTION}}</p>',
  '      </div>',
  '    </div>',
  '  </div>',
  '</section>',
  '',
  '<!-- About Section -->',
  '<section class="about bg-alt py-24">',
  '  <div class="flex items-center gap-16">',
  '    <div class="w-1/2" data-animate="fade-right">',
  '      <img src="about.webp" class="rounded-2xl shadow-xl" />',
  '    </div>',
  '    <div class="w-1/2" data-animate="fade-left">',
  '      <h2 data-animate="text-split">{{ABOUT_TITLE}}</h2>',
  '      <p class="mt-4">{{ABOUT_TEXT}}</p>',
  '    </div>',
  '  </div>',
  '</section>',
  '',
  '<!-- Testimonials -->',
  '<section class="testimonials py-24">',
  '  <h2 class="text-center" data-animate="text-split">',
  '    {{TESTIMONIALS_TITLE}}',
  '  </h2>',
  '  <div class="testimonial-grid mt-16">',
  '    <div class="card" data-animate="fade-up">',
  '      <p>"{{TESTIMONIAL_TEXT}}"</p>',
  '      <span>{{TESTIMONIAL_AUTHOR}}</span>',
  '    </div>',
  '  </div>',
  '</section>',
  '',
  '<!-- Contact -->',
  '<section class="contact py-24" id="contact">',
  '  <h2 data-animate="text-split">{{CONTACT_TITLE}}</h2>',
  '  <form class="mt-12 grid grid-cols-2 gap-6">',
  '    <input type="text" placeholder="Nome" />',
  '    <input type="email" placeholder="Email" />',
  '    <textarea placeholder="Messaggio" class="col-span-2">',
  '    </textarea>',
  '    <button type="submit" data-animate="magnetic">',
  '      Invia Messaggio',
  '    </button>',
  '  </form>',
  '</section>',
  '',
  '<!-- Footer -->',
  '<footer class="py-16 bg-dark">',
  '  <div class="max-w-7xl mx-auto grid grid-cols-4 gap-8">',
  '    <div>',
  '      <img src="logo.svg" class="h-8" />',
  '      <p class="mt-4 text-muted">{{FOOTER_TEXT}}</p>',
  '    </div>',
  '  </div>',
  '</footer>',
  '',
  '<script src="gsap-universal.js"></script>',
  '</body>',
  '</html>',
];

// ============ SYNTAX HIGHLIGHTING ============

function highlightLine(line: string): string {
  if (!line.trim()) return line;

  // HTML comments: <!-- ... -->
  if (/^\s*<!--/.test(line)) {
    return line.replace(/(<!--[\s\S]*?-->)/g, '<span style="color:#64748b">$1</span>');
  }

  // {{...}} placeholders -> cyan
  let result = line.replace(/(\{\{[^}]+\}\})/g, '<span style="color:#22d3ee">$1</span>');

  // CSS lines (property: value pattern inside style blocks)
  if (/^\s+--[\w-]+:/.test(result) || /^\s+[\w-]+\s*:\s*[^{]*[;]?\s*$/.test(result)) {
    // CSS custom properties and regular properties
    result = result.replace(
      /^(\s*)([\w-]+)(\s*:\s*)([^;]*)(;?\s*)$/,
      (_, indent, prop, colon, val, semi) => {
        // Don't re-color if already contains span (from placeholder replacement)
        const coloredVal = val.includes('<span') ? val : `<span style="color:#fb923c">${val}</span>`;
        return `${indent}<span style="color:#60a5fa">${prop}</span>${colon}${coloredVal}${semi}`;
      }
    );
    return result;
  }

  // CSS selectors (lines ending with { or containing * or :root)
  if (/^\s*[\w.*:[\]#,\s-]+\s*\{/.test(result)) {
    result = result.replace(
      /^(\s*)([\w.*:[\]#,\s-]+)(\s*\{)/,
      (_, indent, sel, brace) => `${indent}<span style="color:#c084fc">${sel}</span>${brace}`
    );
    return result;
  }

  // Lines that are just closing braces/tags
  if (/^\s*[}\]<]/.test(result) === false && /^\s*\w/.test(result) && !/</.test(result)) {
    return result;
  }

  // HTML attribute values in quotes -> orange (must be done before attribute names)
  result = result.replace(
    /=("(?:[^"]*)")/g,
    (_, val) => {
      // Don't double-color placeholders
      if (val.includes('<span')) return `=${val}`;
      return `=<span style="color:#fb923c">${val}</span>`;
    }
  );

  // HTML attribute names -> green
  result = result.replace(
    /\s([\w-]+)=/g,
    (match, attr) => ` <span style="color:#4ade80">${attr}</span>=`
  );

  // HTML tags (opening and closing) -> purple
  result = result.replace(
    /(&lt;|<)(\/?)([\w-]+)/g,
    (_, bracket, slash, tag) => `${bracket}${slash}<span style="color:#c084fc">${tag}</span>`
  );

  return result;
}

// ============ TYPES ============

interface PreviewData {
  phase: "analyzing" | "theme_complete" | "content_complete" | "complete";
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

// ============ i18n TEXT ============

const TEXT = {
  it: {
    title: "Generazione in corso...",
    steps: [
      { label: "Analisi stile e testi" },
      { label: "Palette e componenti" },
      { label: "Contenuti e layout" },
      { label: "Generazione immagini" },
      { label: "Assemblaggio finale" },
    ],
    analyzing: "L'AI sta analizzando il tuo business e creando contenuti unici...",
    paletteTitle: "Palette colori selezionata",
    fontHeading: "Font titoli",
    fontBody: "Font corpo",
    contentPreview: "Anteprima contenuti",
    siteReady: "Il tuo sito e' pronto!",
    goToEditor: "Vai all'Editor",
    redirecting: "Reindirizzamento automatico tra pochi secondi...",
    backToDashboard: "Torna al Dashboard",
    errorTitle: "Errore durante la generazione",
    step: "Step",
  },
  en: {
    title: "Generation in progress...",
    steps: [
      { label: "Style & text analysis" },
      { label: "Palette & components" },
      { label: "Content & layout" },
      { label: "Image generation" },
      { label: "Final assembly" },
    ],
    analyzing: "AI is analyzing your business and creating unique content...",
    paletteTitle: "Selected color palette",
    fontHeading: "Heading font",
    fontBody: "Body font",
    contentPreview: "Content preview",
    siteReady: "Your site is ready!",
    goToEditor: "Go to Editor",
    redirecting: "Auto-redirecting in a few seconds...",
    backToDashboard: "Back to Dashboard",
    errorTitle: "Error during generation",
    step: "Step",
  },
};

const STEP_ICONS = [SparklesIcon, PaintBrushIcon, DocumentTextIcon, PhotoIcon, CubeIcon];

// ============ COMPONENT ============

export default function GeneratePage() {
  const params = useParams();
  const router = useRouter();
  const { language } = useLanguage();
  const lang = (language === "en" ? "en" : "it") as "it" | "en";
  const t = TEXT[lang];

  const siteId = Number(params.id);

  // Code animation state
  const [visibleLines, setVisibleLines] = useState<string[]>([]);
  const codeContainerRef = useRef<HTMLDivElement>(null);
  const lineIndexRef = useRef(0);

  // Generation status
  const [status, setStatus] = useState<string>("generating");
  const [step, setStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(5);
  const [percentage, setPercentage] = useState(0);
  const [message, setMessage] = useState("");
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const redirectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Animated percentage for smooth transitions
  const [animatedPercentage, setAnimatedPercentage] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercentage(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  // ---- Code typing animation ----
  useEffect(() => {
    const interval = setInterval(() => {
      if (lineIndexRef.current < CODE_SNIPPETS.length) {
        setVisibleLines(prev => [...prev, CODE_SNIPPETS[lineIndexRef.current]]);
        lineIndexRef.current += 1;
      } else {
        // Loop back from beginning
        lineIndexRef.current = 0;
        setVisibleLines(prev => [...prev, '', '/* ... rebuilding ... */', '']);
      }
    }, 150);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll code panel
  useEffect(() => {
    if (codeContainerRef.current) {
      codeContainerRef.current.scrollTop = codeContainerRef.current.scrollHeight;
    }
  }, [visibleLines]);

  // ---- Status polling ----
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!siteId || isNaN(siteId)) {
      setError(lang === "it" ? "ID sito non valido" : "Invalid site ID");
      return;
    }

    const poll = async () => {
      try {
        const genStatus = await getGenerationStatus(siteId);
        setStep(genStatus.step);
        setTotalSteps(genStatus.total_steps || 5);
        setPercentage(genStatus.percentage);
        setMessage(genStatus.message);
        setStatus(genStatus.status);

        if (genStatus.preview_data) {
          setPreviewData(genStatus.preview_data);
        }

        // Generation complete
        if (!genStatus.is_generating && genStatus.status === "ready") {
          stopPolling();
          setPercentage(100);
          setIsComplete(true);
          setPreviewData(prev => prev ? { ...prev, phase: "complete" } : { phase: "complete" });

          // Auto-redirect after 3 seconds
          redirectTimerRef.current = setTimeout(() => {
            router.push(`/editor/${siteId}`);
          }, 3000);
        }

        // Generation error
        if (!genStatus.is_generating && genStatus.status === "draft" && genStatus.message) {
          stopPolling();
          setError(genStatus.message);
        }
      } catch {
        // Ignore transient errors, keep polling
      }
    };

    // Poll immediately, then every 3 seconds
    poll();
    pollingRef.current = setInterval(poll, 3000);

    return () => {
      stopPolling();
      if (redirectTimerRef.current) clearTimeout(redirectTimerRef.current);
    };
  }, [siteId, stopPolling, router, lang]);

  // ---- Derive phase ----
  const phase = previewData?.phase || "analyzing";

  // ---- SVG progress ----
  const circumference = 2 * Math.PI * 56;
  const strokeDashoffset = circumference * (1 - animatedPercentage / 100);

  // Highlighted lines (memoized)
  const highlightedLines = useMemo(() => {
    return visibleLines.map(line => highlightLine(line));
  }, [visibleLines]);

  // ============ ERROR STATE ============
  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="max-w-md text-center space-y-6 p-8">
          <div className="w-16 h-16 mx-auto rounded-full bg-red-500/20 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white">{t.errorTitle}</h2>
          <p className="text-slate-400">{error}</p>
          <button
            onClick={() => router.push("/dashboard")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white font-medium transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            {t.backToDashboard}
          </button>
        </div>
      </div>
    );
  }

  // ============ MAIN RENDER ============
  return (
    <div className="min-h-screen bg-[#0a0a0f] flex">
      {/* ===== LEFT SIDE: Code Terminal (60%) ===== */}
      <div className="w-[60%] relative flex flex-col border-r border-white/5">
        {/* Grid background pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: "40px 40px",
          }}
        />

        {/* Terminal header */}
        <div className="relative z-10 flex items-center gap-3 px-5 py-3 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-sm">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/60" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <div className="w-3 h-3 rounded-full bg-green-500/60" />
          </div>
          <span className="text-xs text-slate-500 font-mono ml-2">index.html — AI Site Builder</span>
        </div>

        {/* Code content */}
        <div
          ref={codeContainerRef}
          className="relative z-10 flex-1 overflow-y-auto p-0 font-mono text-[13px] leading-6 scrollbar-thin"
          style={{ scrollbarWidth: "thin", scrollbarColor: "#1e293b #0a0a0f" }}
        >
          {highlightedLines.map((html, i) => (
            <div key={i} className="flex hover:bg-white/[0.02] transition-colors">
              {/* Line number */}
              <span className="inline-block w-12 flex-shrink-0 text-right pr-4 text-slate-600 select-none border-r border-white/5 bg-[#0a0a0f]">
                {i + 1}
              </span>
              {/* Code */}
              <span
                className="pl-4 text-slate-300 whitespace-pre"
                dangerouslySetInnerHTML={{ __html: html || "&nbsp;" }}
              />
            </div>
          ))}
          {/* Blinking cursor at the end */}
          <div className="flex">
            <span className="inline-block w-12 flex-shrink-0 text-right pr-4 text-slate-600 select-none border-r border-white/5 bg-[#0a0a0f]">
              {highlightedLines.length + 1}
            </span>
            <span className="pl-4">
              <span className="inline-block w-2 h-5 bg-blue-500 animate-pulse" />
            </span>
          </div>
        </div>
      </div>

      {/* ===== RIGHT SIDE: Progress + Preview (40%) ===== */}
      <div className="w-[40%] flex flex-col overflow-y-auto">
        <div className="flex-1 p-8 flex flex-col items-center gap-8">

          {/* Title */}
          <div className="text-center pt-8">
            <h1 className="text-2xl font-bold text-white mb-2">
              {isComplete ? t.siteReady : t.title}
            </h1>
            {message && !isComplete && (
              <p className="text-sm text-slate-400">{message}</p>
            )}
          </div>

          {/* Circular Progress */}
          <div className="relative w-36 h-36">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
              <circle
                cx="60" cy="60" r="56"
                fill="none"
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="6"
              />
              <circle
                cx="60" cy="60" r="56"
                fill="none"
                stroke="url(#genProgressGradient)"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-1000 ease-out"
              />
              <defs>
                <linearGradient id="genProgressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              {isComplete ? (
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center animate-in zoom-in duration-500">
                  <CheckIcon className="w-6 h-6 text-emerald-400" />
                </div>
              ) : (
                <>
                  <span className="text-3xl font-bold text-white">{Math.round(animatedPercentage)}%</span>
                  <span className="text-xs text-slate-500">
                    {t.step} {step}/{totalSteps}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* 5 Step Indicators */}
          <div className="w-full grid grid-cols-5 gap-1.5">
            {STEP_ICONS.map((Icon, idx) => {
              const stepNum = idx + 1;
              const isActive = step === stepNum;
              const isDone = step > stepNum || isComplete;
              const stepLabel = t.steps[idx]?.label || "";

              return (
                <div
                  key={idx}
                  className={`flex flex-col items-center gap-1.5 p-2 rounded-xl text-center transition-all duration-500 ${
                    isActive
                      ? "bg-blue-500/10 border border-blue-500/30 text-blue-400"
                      : isDone
                      ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                      : "bg-white/[0.02] border border-white/5 text-slate-600"
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center transition-all ${
                      isActive
                        ? "bg-blue-500/20"
                        : isDone
                        ? "bg-emerald-500/20"
                        : "bg-white/5"
                    }`}
                  >
                    {isDone ? (
                      <CheckIcon className="w-3.5 h-3.5" />
                    ) : (
                      <Icon className="w-3.5 h-3.5" />
                    )}
                  </div>
                  <span className="text-[10px] leading-tight">{stepLabel}</span>
                </div>
              );
            })}
          </div>

          {/* Progressive Preview Section */}
          <div className="w-full rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">

            {/* Phase: analyzing - Pulsing orb */}
            {phase === "analyzing" && !isComplete && (
              <div className="p-8 flex flex-col items-center gap-4 animate-in fade-in duration-500">
                <div className="relative">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 animate-pulse" />
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/10 to-violet-500/10 animate-ping absolute inset-0" />
                  <SparklesIcon className="w-8 h-8 text-blue-400 absolute inset-0 m-auto" />
                </div>
                <p className="text-sm text-slate-400 text-center">{t.analyzing}</p>
              </div>
            )}

            {/* Phase: theme_complete - Color palette + fonts */}
            {phase === "theme_complete" && previewData?.colors && (
              <div className="p-6 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
                <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                  <PaintBrushIcon className="w-4 h-4 text-violet-400" />
                  {t.paletteTitle}
                </h4>
                <div className="flex gap-3">
                  {Object.entries(previewData.colors).map(([name, hex]) => (
                    <div key={name} className="flex flex-col items-center gap-1.5">
                      <div
                        className="w-12 h-12 rounded-xl shadow-lg transition-transform hover:scale-110"
                        style={{ backgroundColor: hex }}
                      />
                      <span className="text-[10px] text-slate-500 capitalize">{name}</span>
                    </div>
                  ))}
                </div>
                {previewData.font_heading && (
                  <div className="flex items-center gap-4 pt-2 border-t border-white/5">
                    <div className="text-xs text-slate-500">
                      {t.fontHeading}: <span className="text-slate-300">{previewData.font_heading}</span>
                    </div>
                    <div className="text-xs text-slate-500">
                      {t.fontBody}: <span className="text-slate-300">{previewData.font_body}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Phase: content_complete - Hero title, subtitle, services */}
            {phase === "content_complete" && (
              <div className="p-6 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
                <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                  <DocumentTextIcon className="w-4 h-4 text-emerald-400" />
                  {t.contentPreview}
                </h4>

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
                      style={{ color: previewData?.colors?.primary || "#3b82f6" }}
                    >
                      {previewData.hero_title}
                    </p>
                    {previewData.hero_subtitle && (
                      <p className="text-sm text-slate-400 mb-2">{previewData.hero_subtitle}</p>
                    )}
                    {previewData.hero_cta && (
                      <span
                        className="inline-block px-3 py-1 rounded-lg text-xs text-white"
                        style={{ backgroundColor: previewData?.colors?.primary || "#3b82f6" }}
                      >
                        {previewData.hero_cta}
                      </span>
                    )}
                  </div>
                )}

                {previewData?.services_titles && previewData.services_titles.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {previewData.services_titles.slice(0, 3).map((title, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-lg bg-white/[0.03] border border-white/5 text-center"
                      >
                        <p className="text-xs text-slate-300 truncate">{title}</p>
                      </div>
                    ))}
                  </div>
                )}

                {previewData?.sections && (
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {previewData.sections.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded-full bg-white/5 text-[10px] text-slate-500 capitalize"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Phase: complete - Checkmark + button */}
            {(phase === "complete" || isComplete) && (
              <div className="p-8 flex flex-col items-center gap-4 animate-in fade-in zoom-in duration-500">
                <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <CheckIcon className="w-8 h-8 text-emerald-400" />
                </div>
                <p className="text-lg font-semibold text-emerald-400">{t.siteReady}</p>
                <button
                  onClick={() => router.push(`/editor/${siteId}`)}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-violet-600 hover:opacity-90 rounded-xl font-semibold text-white transition-all flex items-center gap-2"
                >
                  <CubeIcon className="w-5 h-5" />
                  {t.goToEditor}
                </button>
                <p className="text-xs text-slate-500">{t.redirecting}</p>
              </div>
            )}
          </div>

          {/* Spinner for non-complete state */}
          {!isComplete && (
            <div className="flex items-center gap-2 text-slate-500">
              <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
              <span className="text-xs">{message || (lang === "it" ? "Elaborazione..." : "Processing...")}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
