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

// ============ MATRIX RAIN CANVAS ============

function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationWidth = canvas.offsetWidth;
    let animationHeight = canvas.offsetHeight;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      animationWidth = canvas.offsetWidth;
      animationHeight = canvas.offsetHeight;
      canvas.width = animationWidth * dpr;
      canvas.height = animationHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const chars =
      "</> {} () = ; : class div section html css style color font animation data-animate gsap scroll fade transform opacity gradient shadow hover flex grid px py mx my rounded border bg text h1 h2 h3 p a img src alt href #7C3AED #F59E0B #3B82F6 var tailwind responsive design modern beautiful".split(
        " "
      );

    const fontSize = 14;
    const columns = Math.floor(animationWidth / fontSize);
    const drops: number[] = Array(columns)
      .fill(0)
      .map(() => Math.random() * -100);

    const colors = ["#22d3ee", "#4ade80", "#a78bfa", "#60a5fa", "#818cf8"];

    const draw = () => {
      ctx.fillStyle = "rgba(10, 10, 15, 0.05)";
      ctx.fillRect(0, 0, animationWidth, animationHeight);

      for (let i = 0; i < drops.length; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        const color = colors[Math.floor(Math.random() * colors.length)];

        ctx.fillStyle = color;
        ctx.font = `${fontSize}px "JetBrains Mono", "Fira Code", monospace`;
        ctx.globalAlpha = 0.3 + Math.random() * 0.7;
        ctx.fillText(char, i * fontSize, drops[i] * fontSize);
        ctx.globalAlpha = 1;

        if (drops[i] * fontSize > animationHeight && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i] += 0.5 + Math.random() * 0.5;
      }
    };

    const interval = setInterval(draw, 50);
    return () => {
      clearInterval(interval);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ background: "#0a0a0f" }}
      />
      {/* Gradient overlays to soften edges */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-r from-[#0a0a0f] via-transparent to-transparent opacity-80" />
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-[#0a0a0f] via-transparent to-[#0a0a0f] opacity-40" />
    </div>
  );
}

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

// ============ TYPEWRITER HOOK ============

function useTypewriter(text: string, speed = 50) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const prevTextRef = useRef("");

  useEffect(() => {
    if (!text) {
      setDisplayed("");
      setDone(false);
      return;
    }
    // Reset if text changed
    if (text !== prevTextRef.current) {
      prevTextRef.current = text;
      setDisplayed("");
      setDone(false);
    }

    let idx = 0;
    const interval = setInterval(() => {
      idx++;
      if (idx >= text.length) {
        setDisplayed(text);
        setDone(true);
        clearInterval(interval);
      } else {
        setDisplayed(text.slice(0, idx));
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return { displayed, done };
}

// ============ SKELETON WIREFRAME ============

function SkeletonWireframe({ colors }: { colors?: PreviewData["colors"] }) {
  const baseColor = colors?.primary || "#3b82f6";
  const bgTint = colors?.bg ? `${colors.bg}15` : "rgba(255,255,255,0.02)";

  // Generic section shapes for the wireframe
  const sections = [
    { type: "hero", height: "h-24 md:h-32" },
    { type: "content", height: "h-14 md:h-18" },
    { type: "grid", height: "h-16 md:h-20" },
    { type: "content", height: "h-12 md:h-16" },
    { type: "cta", height: "h-10 md:h-12" },
  ];

  return (
    <div className="p-4 md:p-6 space-y-2.5 animate-in fade-in duration-500">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes skeletonShimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .skeleton-shimmer {
          background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.04) 50%, rgba(255,255,255,0) 100%);
          background-size: 200% 100%;
          animation: skeletonShimmer 2s ease-in-out infinite;
        }
      `}} />

      {sections.map((sec, i) => (
        <div
          key={i}
          className={`${sec.height} rounded-lg overflow-hidden relative`}
          style={{
            background: bgTint,
            border: "1px solid rgba(255,255,255,0.05)",
            animationDelay: `${i * 0.15}s`,
          }}
        >
          {/* Shimmer overlay */}
          <div className="skeleton-shimmer absolute inset-0" />

          {/* Wireframe content hints */}
          {sec.type === "hero" && (
            <div className="p-3 md:p-4 space-y-2">
              <div className="h-3 md:h-4 rounded-sm w-2/3" style={{ backgroundColor: `${baseColor}25` }} />
              <div className="h-2 rounded-sm w-1/2 opacity-30 bg-white/10" />
              <div className="h-2 rounded-sm w-1/3 opacity-20 bg-white/10" />
              <div className="mt-2 h-5 md:h-6 rounded-md w-20" style={{ backgroundColor: `${baseColor}20` }} />
            </div>
          )}
          {sec.type === "grid" && (
            <div className="p-3 flex gap-2 h-full items-center">
              {[1, 2, 3].map((n) => (
                <div key={n} className="flex-1 h-3/4 rounded-md" style={{ backgroundColor: `${baseColor}12` }} />
              ))}
            </div>
          )}
          {sec.type === "content" && (
            <div className="p-3 space-y-1.5">
              <div className="h-2.5 rounded-sm w-2/5" style={{ backgroundColor: `${baseColor}18` }} />
              <div className="h-1.5 rounded-sm w-3/4 opacity-20 bg-white/10" />
              <div className="h-1.5 rounded-sm w-1/2 opacity-15 bg-white/10" />
            </div>
          )}
          {sec.type === "cta" && (
            <div className="p-3 flex items-center justify-center h-full">
              <div className="h-5 md:h-6 rounded-md w-28" style={{ backgroundColor: `${baseColor}20` }} />
            </div>
          )}
        </div>
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

  // Mounted state: delay polling until after hydration
  const [mounted, setMounted] = useState(false);

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

        // Photo choices info: backend auto-injects stock photos (non-blocking).
        // User can swap photos later in the editor.
        // No blocking panel during generation — avoids OOM on Render 512MB.

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

  // ---- Typewriter for hero title ----
  const { displayed: typedHeroTitle, done: heroTypeDone } = useTypewriter(
    previewData?.hero_title || "",
    45
  );

  // Photo swap is now handled in the editor after generation completes.
  // No blocking photo choice panel during generation (avoids OOM on Render 512MB).

  // ---- Derive phase ----
  const phase = previewData?.phase || "analyzing";

  // ---- SVG progress ----
  const circumference = 2 * Math.PI * 56;
  const strokeDashoffset = circumference * (1 - animatedPercentage / 100);

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
        {/* ===== LEFT SIDE: Progress + Preview (55%) ===== */}
        <div className="w-full md:w-[55%] flex flex-col overflow-y-auto">
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
            <div className="relative w-36 h-36 md:w-44 md:h-44">
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
            <div className="w-full max-w-lg">
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
            <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">

              {/* Phase: analyzing - Skeleton wireframe */}
              {phase === "analyzing" && !isComplete && (
                <div className="animate-in fade-in duration-500">
                  <div className="px-4 md:px-6 pt-4 pb-2 flex items-center gap-2">
                    <SparklesIcon className="w-4 h-4 text-blue-400 animate-pulse" />
                    <p className="text-xs md:text-sm text-slate-400">{t.analyzing}</p>
                  </div>
                  <SkeletonWireframe colors={previewData?.colors} />
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
                        {typedHeroTitle}
                        {!heroTypeDone && (
                          <span className="inline-block w-[2px] h-[1em] ml-0.5 bg-current animate-pulse align-text-bottom" />
                        )}
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

        {/* ===== RIGHT SIDE: Matrix Rain Effect (45%) ===== */}
        <div className="w-full md:w-[45%] h-[30vh] md:h-auto relative border-t md:border-t-0 md:border-l border-white/5">
          <MatrixRain />
        </div>
      </div>

      {/* Photo swap moved to editor — no blocking overlay during generation */}
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
