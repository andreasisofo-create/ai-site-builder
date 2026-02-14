"use client";

import { Suspense, useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  SparklesIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  PhotoIcon,
  CubeIcon,
  CheckIcon,
  ArrowLeftIcon,
  XMarkIcon,
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
  if (line == null) return '';
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
    generating: "Generazione in corso...",
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
    cancel: "Annulla",
    redirectCountdown: "Redirect tra",
  },
  en: {
    generating: "Generating...",
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
    cancel: "Cancel",
    redirectCountdown: "Redirect in",
  },
};

const STEP_ICONS = [SparklesIcon, PaintBrushIcon, DocumentTextIcon, PhotoIcon, CubeIcon];

// ============ CONFETTI PARTICLES ============

function ConfettiParticles() {
  const particles = useMemo(() => {
    const colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ec4899"];
    return Array.from({ length: 40 }, (_, i) => ({
      id: i,
      left: `${(i * 2.5) % 100}%`,
      color: colors[i % colors.length],
      delay: `${(i * 0.08) % 3}s`,
      duration: `${2 + (i % 3)}s`,
      size: `${3 + (i % 4)}px`,
    }));
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full opacity-0"
          style={{
            left: p.left,
            bottom: "-10px",
            width: p.size,
            height: p.size,
            backgroundColor: p.color,
            animationDelay: p.delay,
            animationDuration: p.duration,
            animationName: "confettiRise",
            animationTimingFunction: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            animationIterationCount: "infinite",
            animationFillMode: "both",
          }}
        />
      ))}
    </div>
  );
}

// ============ INNER COMPONENT ============

function GeneratePageContent() {
  const params = useParams();
  const router = useRouter();
  const { language } = useLanguage();
  const lang = (language === "en" ? "en" : "it") as "it" | "en";
  const t = TEXT[lang];

  // Safely parse site ID from params
  const rawId = params?.id;
  const siteId = rawId ? Number(rawId) : NaN;

  // Mounted state: delay code animation and polling until after hydration
  const [mounted, setMounted] = useState(false);

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
  const [siteName, setSiteName] = useState<string>("");

  // Countdown state for redirect
  const [countdown, setCountdown] = useState(3);

  // Milestone scale animation
  const [milestoneHit, setMilestoneHit] = useState(false);
  const lastMilestoneRef = useRef(0);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const redirectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Animated percentage for smooth transitions
  const [animatedPercentage, setAnimatedPercentage] = useState(0);

  // Set mounted after first render
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercentage(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  // Check for milestone hits (25%, 50%, 75%, 100%)
  useEffect(() => {
    const milestones = [25, 50, 75, 100];
    const currentMilestone = milestones.find(
      (m) => animatedPercentage >= m && lastMilestoneRef.current < m
    );
    if (currentMilestone) {
      lastMilestoneRef.current = currentMilestone;
      setMilestoneHit(true);
      const timer = setTimeout(() => setMilestoneHit(false), 600);
      return () => clearTimeout(timer);
    }
  }, [animatedPercentage]);

  // Countdown timer when complete
  useEffect(() => {
    if (!isComplete) return;
    setCountdown(3);
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isComplete]);

  // ---- Code typing animation (only after mount) ----
  useEffect(() => {
    if (!mounted) return;

    const interval = setInterval(() => {
      if (lineIndexRef.current < CODE_SNIPPETS.length) {
        const idx = lineIndexRef.current;
        setVisibleLines(prev => [...prev, CODE_SNIPPETS[idx] ?? '']);
        lineIndexRef.current = idx + 1;
      } else {
        // Loop back from beginning
        lineIndexRef.current = 0;
        setVisibleLines(prev => [...prev, '', '/* ... rebuilding ... */', '']);
      }
    }, 150);

    return () => clearInterval(interval);
  }, [mounted]);

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
    if (!mounted) return;

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

        // Try to extract site name from response (may not exist in type but backend could send it)
        const statusAny = genStatus as unknown as Record<string, unknown>;
        if (statusAny.site_name && typeof statusAny.site_name === "string") {
          setSiteName(statusAny.site_name);
        }

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
  }, [mounted, siteId, stopPolling, router, lang]);

  // ---- Derive phase ----
  const phase = previewData?.phase || "analyzing";

  // ---- SVG progress ----
  const circumference = 2 * Math.PI * 56;
  const strokeDashoffset = circumference * (1 - animatedPercentage / 100);

  // Highlighted lines (memoized)
  const highlightedLines = useMemo(() => {
    return visibleLines.map(line => highlightLine(line ?? ''));
  }, [visibleLines]);

  // ============ ERROR STATE ============
  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex flex-col">
        {/* Header bar */}
        <header className="bg-[#0a0a0f] border-b border-white/5 h-14 px-4 md:px-6 flex items-center shrink-0">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            <span className="text-sm font-semibold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
              Site Builder
            </span>
          </Link>
        </header>

        <div className="flex-1 flex items-center justify-center px-4">
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
      </div>
    );
  }

  // ============ MAIN RENDER ============
  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col">
      {/* Confetti keyframes */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes confettiRise {
          0% { opacity: 0; transform: translateY(0) rotate(0deg) scale(1); }
          10% { opacity: 1; }
          50% { opacity: 0.8; transform: translateY(-50vh) rotate(180deg) scale(1.2); }
          100% { opacity: 0; transform: translateY(-100vh) rotate(360deg) scale(0.5); }
        }
      `}} />

      {/* ===== TOP HEADER BAR ===== */}
      <header className="bg-[#0a0a0f] border-b border-white/5 h-14 px-4 md:px-6 flex items-center shrink-0 z-30">
        {/* Left: Back arrow + logo */}
        <Link
          href="/dashboard"
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors shrink-0"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          <span className="text-sm font-semibold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent hidden sm:inline">
            Site Builder
          </span>
        </Link>

        {/* Center: Current status message */}
        <div className="flex-1 flex justify-center min-w-0 px-2">
          <div className="flex items-center gap-2 max-w-xs md:max-w-md truncate">
            {!isComplete ? (
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shrink-0" />
            ) : (
              <div className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
            )}
            <span className="text-xs text-slate-400 truncate">
              {isComplete ? t.siteReady : (message || t.title)}
            </span>
            {!isComplete && (
              <span className="text-xs text-slate-600 font-mono shrink-0">{Math.round(animatedPercentage)}%</span>
            )}
          </div>
        </div>

        {/* Right: Cancel */}
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors shrink-0"
        >
          <XMarkIcon className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">{t.cancel}</span>
        </Link>
      </header>

      {/* ===== MAIN CONTENT ===== */}
      <div className="flex-1 flex flex-col md:flex-row min-h-0">
        {/* ===== LEFT SIDE: Code Terminal ===== */}
        <div className="w-full md:w-[60%] relative flex flex-col border-b md:border-b-0 md:border-r border-white/5 max-h-[40vh] md:max-h-none">
          {/* Grid background pattern */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
              backgroundSize: "40px 40px",
            }}
          />

          {/* File tabs bar (VS Code style) */}
          <div className="relative z-10 flex items-stretch border-b border-white/5 bg-[#0c0c14]">
            {/* Active tab */}
            <div className="flex items-center gap-2 px-3 md:px-4 py-2.5 bg-[#0a0a0f] border-r border-white/5 border-b-2 border-b-blue-500">
              <svg className="w-3.5 h-3.5 text-orange-400 shrink-0" viewBox="0 0 16 16" fill="currentColor">
                <path d="M1.5 0h13l.5.5v15l-.5.5h-13l-.5-.5V.5L1.5 0zM2 1v14h12V1H2z"/>
                <path d="M4 4h8v1H4V4zm0 3h8v1H4V7zm0 3h5v1H4v-1z"/>
              </svg>
              <span className="text-xs text-slate-300 font-mono">index.html</span>
              <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            </div>
            {/* Inactive tab */}
            <div className="flex items-center gap-2 px-3 md:px-4 py-2.5 bg-[#0c0c14] border-r border-white/5 opacity-40 hidden sm:flex">
              <svg className="w-3.5 h-3.5 text-blue-400 shrink-0" viewBox="0 0 16 16" fill="currentColor">
                <path d="M1.5 0h13l.5.5v15l-.5.5h-13l-.5-.5V.5L1.5 0zM2 1v14h12V1H2z"/>
              </svg>
              <span className="text-xs text-slate-500 font-mono">styles.css</span>
            </div>
            {/* Inactive tab */}
            <div className="flex items-center gap-2 px-3 md:px-4 py-2.5 bg-[#0c0c14] opacity-40 hidden md:flex">
              <svg className="w-3.5 h-3.5 text-yellow-400 shrink-0" viewBox="0 0 16 16" fill="currentColor">
                <path d="M1.5 0h13l.5.5v15l-.5.5h-13l-.5-.5V.5L1.5 0zM2 1v14h12V1H2z"/>
              </svg>
              <span className="text-xs text-slate-500 font-mono">gsap-universal.js</span>
            </div>
            {/* Spacer */}
            <div className="flex-1 bg-[#0c0c14]" />
            {/* Traffic lights */}
            <div className="flex items-center gap-1.5 px-3 md:px-4 bg-[#0c0c14]">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-500/50" />
            </div>
          </div>

          {/* Code content */}
          <div
            ref={codeContainerRef}
            className="relative z-10 flex-1 overflow-y-auto p-0 font-mono text-[12px] md:text-[13px] leading-6 scrollbar-thin"
            style={{ scrollbarWidth: "thin", scrollbarColor: "#1e293b #0a0a0f" }}
          >
            {highlightedLines.map((html, i) => (
              <div key={i} className="flex hover:bg-white/[0.02] transition-colors group">
                {/* Line number */}
                <span className="inline-block w-10 md:w-14 flex-shrink-0 text-right pr-3 md:pr-5 py-0 text-slate-700 group-hover:text-slate-500 select-none border-r border-white/[0.04] bg-[#08080d] font-mono tabular-nums transition-colors text-[11px] md:text-[12px]">
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
              <span className="inline-block w-10 md:w-14 flex-shrink-0 text-right pr-3 md:pr-5 text-slate-700 select-none border-r border-white/[0.04] bg-[#08080d] font-mono tabular-nums text-[11px] md:text-[12px]">
                {highlightedLines.length + 1}
              </span>
              <span className="pl-4">
                <span className="inline-block w-2 h-5 bg-blue-500 animate-pulse" />
              </span>
            </div>
          </div>

          {/* Bottom glow where new code appears */}
          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-blue-500/[0.06] to-transparent pointer-events-none z-20" />
          {/* Scanline effect */}
          <div
            className="absolute bottom-0 left-0 right-0 h-24 pointer-events-none z-20 opacity-30"
            style={{
              background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(59,130,246,0.03) 2px, rgba(59,130,246,0.03) 4px)",
            }}
          />
        </div>

        {/* ===== RIGHT SIDE: Progress + Preview ===== */}
        <div className="w-full md:w-[40%] flex flex-col overflow-y-auto">
          <div className="flex-1 p-4 md:p-8 flex flex-col items-center gap-5 md:gap-8">

            {/* Title */}
            <div className="text-center pt-2 md:pt-8">
              <h1 className="text-xl md:text-2xl font-bold text-white mb-2">
                {isComplete ? t.siteReady : t.title}
              </h1>
              {message && !isComplete && (
                <p className="text-xs md:text-sm text-slate-400">{message}</p>
              )}
            </div>

            {/* Circular Progress with glow */}
            <div className="relative w-36 h-36 md:w-40 md:h-40">
              {/* Pulsing glow behind the circle */}
              <div
                className="absolute -inset-3 rounded-full blur-2xl opacity-25 animate-pulse"
                style={{
                  background: "conic-gradient(from 0deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6)",
                }}
              />
              <svg
                className={`w-full h-full -rotate-90 relative z-10 transition-transform duration-500 ease-out ${
                  milestoneHit ? "scale-110" : "scale-100"
                }`}
                viewBox="0 0 120 120"
              >
                <circle
                  cx="60" cy="60" r="56"
                  fill="none"
                  stroke="rgba(255,255,255,0.05)"
                  strokeWidth="5"
                />
                <circle
                  cx="60" cy="60" r="56"
                  fill="none"
                  stroke="url(#genProgressGradient)"
                  strokeWidth="5"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  className="transition-all duration-1000 ease-out"
                  style={{
                    filter: "drop-shadow(0 0 6px rgba(139, 92, 246, 0.5))",
                  }}
                />
                <defs>
                  <linearGradient id="genProgressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="50%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
                {isComplete ? (
                  <div className="w-12 h-12 md:w-14 md:h-14 rounded-full bg-emerald-500/20 flex items-center justify-center animate-in zoom-in duration-500">
                    <CheckIcon className="w-6 h-6 md:w-7 md:h-7 text-emerald-400" />
                  </div>
                ) : (
                  <>
                    <span className="text-3xl md:text-4xl font-bold text-white">{Math.round(animatedPercentage)}%</span>
                    <span className="text-[10px] md:text-xs text-slate-500">
                      {t.step} {step}/{totalSteps}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* 5 Step Indicators with connecting lines */}
            <div className="w-full">
              <div className="flex items-start justify-between relative">
                {/* Background connecting line */}
                <div className="absolute top-[14px] left-[10%] right-[10%] h-[2px] bg-white/5 z-0" />
                {/* Active connecting line (colored) */}
                <div
                  className="absolute top-[14px] left-[10%] h-[2px] z-[1] transition-all duration-700 ease-out"
                  style={{
                    width: `${Math.min(100, Math.max(0, ((step - 1) / (totalSteps - 1)) * 80))}%`,
                    background: "linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4)",
                  }}
                />

                {STEP_ICONS.map((Icon, idx) => {
                  const stepNum = idx + 1;
                  const isActive = step === stepNum;
                  const isDone = step > stepNum || isComplete;
                  const stepLabel = t.steps[idx]?.label || "";

                  return (
                    <div
                      key={idx}
                      className="flex flex-col items-center gap-1.5 relative z-10"
                      style={{ width: `${100 / totalSteps}%` }}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center transition-all duration-500 ${
                          isActive
                            ? "bg-blue-500/30 ring-2 ring-blue-500/50 text-blue-400 scale-110"
                            : isDone
                            ? "bg-emerald-500/20 text-emerald-400"
                            : "bg-[#0e0e16] border border-white/10 text-slate-600"
                        }`}
                      >
                        {isDone ? (
                          <CheckIcon className="w-3.5 h-3.5" />
                        ) : (
                          <Icon className="w-3.5 h-3.5" />
                        )}
                      </div>
                      <span
                        className={`text-[8px] md:text-[10px] leading-tight text-center transition-colors duration-500 max-w-[60px] md:max-w-none ${
                          isActive
                            ? "text-blue-400"
                            : isDone
                            ? "text-emerald-400"
                            : "text-slate-600"
                        }`}
                      >
                        {stepLabel}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Progressive Preview Section */}
            <div className="w-full rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">

              {/* Phase: analyzing - Pulsing orb */}
              {phase === "analyzing" && !isComplete && (
                <div className="p-6 md:p-8 flex flex-col items-center gap-4 animate-in fade-in duration-500">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 animate-pulse" />
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/10 to-violet-500/10 animate-ping absolute inset-0" />
                    <SparklesIcon className="w-8 h-8 text-blue-400 absolute inset-0 m-auto" />
                  </div>
                  <p className="text-xs md:text-sm text-slate-400 text-center">{t.analyzing}</p>
                </div>
              )}

              {/* Phase: theme_complete - Color palette + fonts */}
              {phase === "theme_complete" && previewData?.colors && (
                <div className="p-4 md:p-6 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
                  <h4 className="text-xs md:text-sm font-medium text-slate-300 flex items-center gap-2">
                    <PaintBrushIcon className="w-4 h-4 text-violet-400" />
                    {t.paletteTitle}
                  </h4>
                  <div className="flex gap-2 md:gap-3 flex-wrap">
                    {Object.entries(previewData.colors).map(([name, hex]) => (
                      <div key={name} className="flex flex-col items-center gap-1.5">
                        <div
                          className="w-10 h-10 md:w-12 md:h-12 rounded-xl shadow-lg transition-transform hover:scale-110"
                          style={{ backgroundColor: hex }}
                        />
                        <span className="text-[9px] md:text-[10px] text-slate-500 capitalize">{name}</span>
                      </div>
                    ))}
                  </div>
                  {previewData.font_heading && (
                    <div className="flex items-center gap-3 md:gap-4 pt-2 border-t border-white/5 flex-wrap">
                      <div className="text-[10px] md:text-xs text-slate-500">
                        {t.fontHeading}: <span className="text-slate-300">{previewData.font_heading}</span>
                      </div>
                      <div className="text-[10px] md:text-xs text-slate-500">
                        {t.fontBody}: <span className="text-slate-300">{previewData.font_body}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Phase: content_complete - Hero title, subtitle, services */}
              {phase === "content_complete" && (
                <div className="p-4 md:p-6 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
                  <h4 className="text-xs md:text-sm font-medium text-slate-300 flex items-center gap-2">
                    <DocumentTextIcon className="w-4 h-4 text-emerald-400" />
                    {t.contentPreview}
                  </h4>

                  {previewData?.hero_title && (
                    <div
                      className="p-3 md:p-4 rounded-xl border border-white/10"
                      style={{
                        background: previewData?.colors
                          ? `linear-gradient(135deg, ${previewData.colors.primary}15, ${previewData.colors.secondary}15)`
                          : "rgba(255,255,255,0.02)",
                      }}
                    >
                      <p
                        className="text-base md:text-lg font-bold mb-1"
                        style={{ color: previewData?.colors?.primary || "#3b82f6" }}
                      >
                        {previewData.hero_title}
                      </p>
                      {previewData.hero_subtitle && (
                        <p className="text-xs md:text-sm text-slate-400 mb-2">{previewData.hero_subtitle}</p>
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
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {previewData.services_titles.slice(0, 3).map((title, i) => (
                        <div
                          key={i}
                          className="p-2 md:p-3 rounded-lg bg-white/[0.03] border border-white/5 text-center"
                        >
                          <p className="text-[10px] md:text-xs text-slate-300 truncate">{title}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {previewData?.sections && (
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {previewData.sections.map((s) => (
                        <span
                          key={s}
                          className="px-2 py-0.5 rounded-full bg-white/5 text-[9px] md:text-[10px] text-slate-500 capitalize"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Phase: complete - Celebration */}
              {(phase === "complete" || isComplete) && (
                <div className="relative p-6 md:p-8 flex flex-col items-center gap-5 animate-in fade-in zoom-in duration-500 overflow-hidden">
                  {/* Confetti particles */}
                  <ConfettiParticles />

                  {/* Mini preview thumbnail */}
                  {previewData?.colors && (
                    <div
                      className="relative z-10 w-full max-w-[220px] md:max-w-[260px] h-28 md:h-36 rounded-xl border border-white/10 overflow-hidden shadow-2xl"
                      style={{
                        background: previewData.colors.bg || "#faf7f2",
                      }}
                    >
                      {/* Mini site wireframe */}
                      <div className="p-3">
                        <div
                          className="h-3 rounded-sm w-3/4 mb-1.5"
                          style={{ backgroundColor: previewData.colors.primary }}
                        />
                        <div className="h-1.5 rounded-sm w-1/2 mb-3 opacity-40" style={{ backgroundColor: previewData.colors.text || "#333" }} />
                        <div
                          className="h-4 rounded-sm w-16 mb-3"
                          style={{ backgroundColor: previewData.colors.accent || previewData.colors.primary }}
                        />
                        <div className="flex gap-1.5">
                          <div className="flex-1 h-8 rounded-sm" style={{ backgroundColor: `${previewData.colors.secondary}20` }} />
                          <div className="flex-1 h-8 rounded-sm" style={{ backgroundColor: `${previewData.colors.primary}20` }} />
                          <div className="flex-1 h-8 rounded-sm" style={{ backgroundColor: `${previewData.colors.accent || previewData.colors.secondary}20` }} />
                        </div>
                      </div>
                      {/* Gloss overlay */}
                      <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
                    </div>
                  )}

                  {/* Check icon */}
                  <div className="relative z-10 w-14 h-14 md:w-16 md:h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <CheckIcon className="w-7 h-7 md:w-8 md:h-8 text-emerald-400" />
                  </div>

                  <p className="relative z-10 text-base md:text-lg font-semibold text-emerald-400">{t.siteReady}</p>

                  {/* Prominent "Go to Editor" button */}
                  <button
                    onClick={() => router.push(`/editor/${siteId}`)}
                    className="relative z-10 group px-8 py-3.5 bg-gradient-to-r from-blue-600 via-violet-600 to-cyan-600 rounded-xl font-semibold text-white transition-all flex items-center gap-2 shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-[1.03] active:scale-[0.98]"
                  >
                    {/* Pulse ring behind button */}
                    <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-600 via-violet-600 to-cyan-600 animate-ping opacity-20 pointer-events-none" />
                    <CubeIcon className="w-5 h-5 relative" />
                    <span className="relative">{t.goToEditor}</span>
                  </button>

                  {/* Countdown */}
                  <p className="relative z-10 text-xs text-slate-500">
                    {t.redirectCountdown} {countdown}...
                  </p>
                </div>
              )}
            </div>

            {/* Spinner for non-complete state */}
            {!isComplete && (
              <div className="flex items-center gap-2 text-slate-500">
                <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
                <span className="text-[10px] md:text-xs">{message || (lang === "it" ? "Elaborazione..." : "Processing...")}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============ EXPORTED PAGE WITH SUSPENSE BOUNDARY ============

export default function GeneratePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
      </div>
    }>
      <GeneratePageContent />
    </Suspense>
  );
}
