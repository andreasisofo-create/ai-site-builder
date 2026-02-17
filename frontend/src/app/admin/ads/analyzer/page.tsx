"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Globe,
  Search,
  Loader2,
  Building2,
  Target,
  Briefcase,
  MessageSquare,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Lightbulb,
  Sparkles,
  ArrowRight,
  RotateCcw,
  Download,
} from "lucide-react";

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
function adminFetch(path: string, options: RequestInit = {}) {
  const token = sessionStorage.getItem("admin_token");
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  }).then((res) => {
    if (res.status === 401) {
      sessionStorage.removeItem("admin_token");
      throw new Error("SESSION_EXPIRED");
    }
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  });
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface Service {
  name: string;
  description: string;
  price: string | null;
}

interface AnalysisResult {
  business_name: string;
  business_type: string;
  sector: string;
  value_proposition: string;
  target_audience: string[];
  services: Service[];
  tone_of_voice: string;
  tone_keywords: string[];
  strengths: string[];
  weaknesses: string[];
  cta_list: string[];
  site_structure: string[];
  tech_detected: string[];
  tech_score: number;
  seo_score: number;
  mobile_score: number;
  suggested_campaign_type: string;
  suggested_platform: string;
  ai_suggestions: string[];
  analyzed_url: string;
  analyzed_at: string;
}

// ---------------------------------------------------------------------------
// Score Circle Component
// ---------------------------------------------------------------------------
function ScoreCircle({
  value,
  label,
  delay,
}: {
  value: number;
  label: string;
  delay: number;
}) {
  const [displayed, setDisplayed] = useState(0);
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayed / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => {
      let current = 0;
      const interval = setInterval(() => {
        current += 1;
        if (current >= value) {
          setDisplayed(value);
          clearInterval(interval);
        } else {
          setDisplayed(current);
        }
      }, 15);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  const color =
    displayed < 40
      ? "text-red-400 stroke-red-400"
      : displayed < 70
        ? "text-yellow-400 stroke-yellow-400"
        : "text-emerald-400 stroke-emerald-400";

  const bgStroke =
    displayed < 40
      ? "stroke-red-400/10"
      : displayed < 70
        ? "stroke-yellow-400/10"
        : "stroke-emerald-400/10";

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-24 h-24">
        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            className={bgStroke}
            strokeWidth="6"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            className={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.3s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-xl font-bold ${color.split(" ")[0]}`}>
            {displayed}
          </span>
        </div>
      </div>
      <span className="text-xs text-gray-400 font-medium">{label}</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Loading Messages
// ---------------------------------------------------------------------------
const LOADING_MESSAGES = [
  "Scaricando il sito...",
  "Analizzando contenuti...",
  "Estraendo informazioni chiave...",
  "Generando report AI...",
  "Elaborando suggerimenti...",
];

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------
export default function WebsiteAnalyzerPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0]);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [visibleCards, setVisibleCards] = useState(0);
  const resultRef = useRef<HTMLDivElement>(null);

  // Cycle loading messages
  useEffect(() => {
    if (!loading) return;
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % LOADING_MESSAGES.length;
      setLoadingMsg(LOADING_MESSAGES[idx]);
    }, 3000);
    return () => clearInterval(interval);
  }, [loading]);

  // Stagger card appearance
  useEffect(() => {
    if (!result) return;
    setVisibleCards(0);
    const total = 7;
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setVisibleCards(i);
      if (i >= total) clearInterval(interval);
    }, 150);
    return () => clearInterval(interval);
  }, [result]);

  // Scroll to results
  useEffect(() => {
    if (result && resultRef.current) {
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 300);
    }
  }, [result]);

  const handleAnalyze = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const resp = await adminFetch("/api/ads/analyze-website", {
        method: "POST",
        body: JSON.stringify({ url: url.trim() }),
      });
      if (resp.success && resp.data) {
        setResult(resp.data);
      } else {
        setError(resp.detail || "Errore nell'analisi");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Errore sconosciuto";
      if (message === "SESSION_EXPIRED") {
        router.push("/admin");
        return;
      }
      setError(`Errore: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setUrl("");
    setResult(null);
    setError("");
  };

  const handleExport = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `analisi-${result.business_name || "sito"}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const cardClass = (idx: number) =>
    `bg-[#141420] border border-white/5 rounded-xl p-5 transition-all duration-500 ${
      visibleCards > idx
        ? "opacity-100 translate-y-0"
        : "opacity-0 translate-y-4"
    }`;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-orange-600 flex items-center justify-center">
            <Globe className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Analizza Sito Web</h1>
            <p className="text-sm text-gray-400">
              Modulo Investigatore &mdash; Analisi AI completa di qualsiasi sito
            </p>
          </div>
        </div>
      </div>

      {/* URL Input */}
      <div className="bg-[#141420] border border-white/5 rounded-xl p-6">
        <label className="block text-sm text-gray-400 mb-3 font-medium">
          Inserisci URL del sito da analizzare
        </label>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="url"
              placeholder="https://www.esempio.it"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleAnalyze()}
              disabled={loading}
              className="w-full bg-[#0a0a0f] border border-white/10 rounded-lg pl-11 pr-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20 transition-colors disabled:opacity-50"
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-gradient-to-r from-violet-500 to-orange-600 text-white font-semibold rounded-lg hover:from-violet-600 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Search className="w-5 h-5" />
            )}
            {loading ? "Analizzando..." : "Analizza"}
          </button>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="mt-6 flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
            <span className="text-violet-400 text-sm font-medium animate-pulse">
              {loadingMsg}
            </span>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <span className="text-red-400 text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div ref={resultRef} className="space-y-4">
          {/* Analyzed URL banner */}
          <div className="flex items-center justify-between bg-[#141420] border border-violet-500/20 rounded-xl px-5 py-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-400" />
              <span className="text-violet-400 font-medium text-sm">
                Report per: {result.analyzed_url}
              </span>
            </div>
            <span className="text-xs text-gray-500">
              {new Date(result.analyzed_at).toLocaleString("it-IT")}
            </span>
          </div>

          {/* Row 1 - Business Identity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Business Profile */}
            <div className={cardClass(0)}>
              <div className="flex items-center gap-2 mb-4">
                <Building2 className="w-4 h-4 text-violet-400" />
                <h3 className="text-white font-semibold text-sm">Profilo Business</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <span className="text-2xl font-bold text-white">{result.business_name}</span>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <span className="px-2 py-1 bg-violet-500/10 text-violet-400 rounded text-xs font-medium">
                    {result.business_type}
                  </span>
                  <span className="px-2 py-1 bg-white/5 text-gray-300 rounded text-xs">
                    {result.sector}
                  </span>
                </div>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {result.value_proposition}
                </p>
              </div>
            </div>

            {/* Target Audience */}
            <div className={cardClass(0)}>
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-4 h-4 text-blue-400" />
                <h3 className="text-white font-semibold text-sm">Target Audience</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {result.target_audience.map((seg, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-blue-500/10 text-blue-300 rounded-lg text-sm border border-blue-500/10"
                  >
                    {seg}
                  </span>
                ))}
              </div>
              {result.cta_list.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/5">
                  <span className="text-xs text-gray-500 block mb-2">CTA Principali</span>
                  <div className="flex flex-wrap gap-2">
                    {result.cta_list.map((cta, i) => (
                      <span key={i} className="px-2 py-1 bg-white/5 text-gray-300 rounded text-xs">
                        &ldquo;{cta}&rdquo;
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Row 2 - Services & Tone */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Services */}
            <div className={cardClass(1)}>
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="w-4 h-4 text-purple-400" />
                <h3 className="text-white font-semibold text-sm">Servizi / Prodotti</h3>
              </div>
              <div className="space-y-2">
                {result.services.map((svc, i) => (
                  <div key={i} className="flex items-start gap-3 p-2 rounded-lg bg-white/[0.02]">
                    <div className="w-6 h-6 rounded bg-purple-500/10 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-xs text-purple-400 font-bold">{i + 1}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-white text-sm font-medium">{svc.name}</span>
                        {svc.price && (
                          <span className="text-xs text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            {svc.price}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-500 text-xs mt-0.5">{svc.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tone of Voice */}
            <div className={cardClass(1)}>
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-4 h-4 text-pink-400" />
                <h3 className="text-white font-semibold text-sm">Tone of Voice</h3>
              </div>
              <div className="mb-4">
                <span className="px-3 py-1.5 bg-pink-500/10 text-pink-300 rounded-lg text-sm font-medium border border-pink-500/10">
                  {result.tone_of_voice}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {result.tone_keywords.map((kw, i) => (
                  <span key={i} className="px-2 py-1 bg-white/5 text-gray-400 rounded text-xs">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Row 3 - SWOT */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Strengths */}
            <div className={cardClass(2)}>
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <h3 className="text-white font-semibold text-sm">Punti di Forza</h3>
              </div>
              <ul className="space-y-2">
                {result.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                    <span className="text-gray-300">{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Weaknesses */}
            <div className={cardClass(2)}>
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <h3 className="text-white font-semibold text-sm">Punti di Debolezza</h3>
              </div>
              <ul className="space-y-2">
                {result.weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
                    <span className="text-gray-300">{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Row 4 - Technical Scores */}
          <div className={cardClass(3)}>
            <div className="flex items-center gap-2 mb-6">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h3 className="text-white font-semibold text-sm">Analisi Tecnica</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex justify-center gap-8">
                <ScoreCircle value={result.tech_score} label="Tech Score" delay={0} />
                <ScoreCircle value={result.seo_score} label="SEO Score" delay={200} />
                <ScoreCircle value={result.mobile_score} label="Mobile Score" delay={400} />
              </div>
              <div className="space-y-4">
                <div>
                  <span className="text-xs text-gray-500 block mb-2">Tech Stack Rilevato</span>
                  <div className="flex flex-wrap gap-2">
                    {result.tech_detected.map((tech, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-cyan-500/10 text-cyan-300 rounded text-xs border border-cyan-500/10"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block mb-2">Struttura Sito</span>
                  <div className="flex flex-wrap gap-2">
                    {result.site_structure.map((sec, i) => (
                      <span key={i} className="px-2 py-1 bg-white/5 text-gray-400 rounded text-xs">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Row 5 - AI Suggestions */}
          <div className={cardClass(4)}>
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-4 h-4 text-violet-400" />
              <h3 className="text-white font-semibold text-sm">Suggerimenti AI per le Ads</h3>
            </div>

            <div className="flex gap-2 mb-4">
              <span className="px-3 py-1 bg-violet-500/10 text-violet-400 rounded-lg text-xs font-medium border border-violet-500/10">
                Tipo: {result.suggested_campaign_type}
              </span>
              <span className="px-3 py-1 bg-violet-500/10 text-violet-400 rounded-lg text-xs font-medium border border-violet-500/10">
                Piattaforma: {result.suggested_platform}
              </span>
            </div>

            <ol className="space-y-2">
              {result.ai_suggestions.map((sugg, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="w-6 h-6 rounded-full bg-violet-500/10 flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-xs text-violet-400 font-bold">{i + 1}</span>
                  </span>
                  <span className="text-gray-300">{sugg}</span>
                </li>
              ))}
            </ol>

            <div className="mt-5 pt-4 border-t border-white/5">
              <button
                onClick={() => router.push("/admin/ads/wizard")}
                className="px-4 py-2 bg-gradient-to-r from-violet-500 to-orange-600 text-white text-sm font-semibold rounded-lg hover:from-violet-600 hover:to-orange-700 transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Crea Campagna
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Row 6 - Actions */}
          <div className={cardClass(5)}>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-white/5 text-gray-300 text-sm rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2 border border-white/5"
              >
                <RotateCcw className="w-4 h-4" />
                Analizza Altro Sito
              </button>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-white/5 text-gray-300 text-sm rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2 border border-white/5"
              >
                <Download className="w-4 h-4" />
                Esporta Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
