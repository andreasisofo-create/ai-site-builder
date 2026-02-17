"use client";

import { useState } from "react";
import { API_BASE } from "@/lib/api";
import {
  Image,
  Video,
  FolderOpen,
  Sparkles,
  Download,
  Loader2,
  ChevronDown,
  ExternalLink,
  Play,
  AlertCircle,
  Settings,
  Wand2,
  ImagePlus,
} from "lucide-react";

// ---------------------------------------------------------------------------
// API helper (admin token)
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
// Constants
// ---------------------------------------------------------------------------
const IMAGE_FORMATS = [
  { value: "1:1", label: "Feed 1:1", size: "1080 x 1080" },
  { value: "9:16", label: "Stories / Reels 9:16", size: "1080 x 1920" },
  { value: "16:9", label: "Landscape 16:9", size: "1920 x 1080" },
  { value: "banner", label: "Display Banner", size: "728 x 90" },
];

const IMAGE_STYLES = [
  { value: "photographic", label: "Fotografico Realistico" },
  { value: "illustration", label: "Illustrazione Moderna" },
  { value: "minimal", label: "Minimal / Flat Design" },
  { value: "luxury", label: "Luxury / Premium" },
  { value: "food", label: "Food Photography" },
  { value: "product", label: "Product Shot" },
];

const PROMPT_TEMPLATES = [
  {
    emoji: "\uD83C\uDF55",
    label: "Ristorante",
    prompt:
      "Piatto gourmet su tavolo elegante, illuminazione calda, vista dall'alto, food photography professionale",
  },
  {
    emoji: "\uD83D\uDCAA",
    label: "Fitness",
    prompt:
      "Persona sportiva in palestra moderna, luce drammatica, energia e motivazione",
  },
  {
    emoji: "\uD83C\uDFE0",
    label: "Immobiliare",
    prompt:
      "Interno appartamento moderno e luminoso, design minimal, ampi spazi",
  },
  {
    emoji: "\uD83D\uDCBB",
    label: "SaaS",
    prompt:
      "Dashboard moderna su laptop, sfondo gradient, clean tech aesthetic",
  },
  {
    emoji: "\uD83D\uDC88",
    label: "Beauty",
    prompt:
      "Trattamento beauty in ambiente spa elegante, colori pastello, relax",
  },
];

const VIDEO_TEMPLATES = [
  { value: "testimonial", label: "Video Testimonial" },
  { value: "product", label: "Product Showcase" },
  { value: "before-after", label: "Before / After" },
  { value: "promo", label: "Promo Countdown" },
];

const EXTERNAL_TOOLS = [
  {
    name: "Higgsfield AI",
    url: "https://higgsfield.ai",
    description:
      "AI video cinematografici, avatar parlanti, effetti premium",
    badge: "Nessuna API - Uso Manuale",
    badgeColor: "text-gray-400 bg-white/5",
    buttonLabel: "Apri Higgsfield",
    external: true,
  },
  {
    name: "Weavy AI",
    url: "https://www.weavy.ai/",
    description:
      "Piattaforma node-based con Flux Pro, Runway Gen-4, Stable Diffusion",
    badge: "Nessuna API - Uso Manuale",
    badgeColor: "text-gray-400 bg-white/5",
    buttonLabel: "Apri Weavy",
    external: true,
  },
  {
    name: "Replicate",
    url: "https://replicate.com",
    description: "Modelli video open-source (Wan 2.1, etc.)",
    badge: "API Disponibile",
    badgeColor: "text-emerald-400 bg-emerald-500/10",
    buttonLabel: "Configura API",
    external: false,
    internalUrl: "/admin/ads/setup",
  },
  {
    name: "RunwayML",
    url: "https://runwayml.com",
    description: "Gen-3 Alpha, video AI professionali",
    badge: "API Enterprise",
    badgeColor: "text-amber-400 bg-amber-500/10",
    buttonLabel: "Apri Runway",
    external: true,
  },
];

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------
type Tab = "image" | "video" | "library";

const TABS: { id: Tab; label: string; icon: typeof Image }[] = [
  { id: "image", label: "Generatore Immagini", icon: Image },
  { id: "video", label: "Video Creator", icon: Video },
  { id: "library", label: "Libreria Creativi", icon: FolderOpen },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ContentCreatorPage() {
  const [activeTab, setActiveTab] = useState<Tab>("image");

  // Image generator state
  const [prompt, setPrompt] = useState("");
  const [format, setFormat] = useState("1:1");
  const [style, setStyle] = useState("photographic");
  const [overlayEnabled, setOverlayEnabled] = useState(false);
  const [overlayText, setOverlayText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<{
    status: string;
    message: string;
    setup_url?: string;
    image_url?: string;
  } | null>(null);

  // Video state
  const [videoTemplate, setVideoTemplate] = useState("testimonial");

  // -------------------------------------------------------------------------
  // Generate image
  // -------------------------------------------------------------------------
  async function handleGenerate() {
    if (!prompt.trim()) return;
    setGenerating(true);
    setResult(null);
    try {
      const data = await adminFetch("/api/ads/generate-image", {
        method: "POST",
        body: JSON.stringify({
          prompt: prompt.trim(),
          format,
          style,
          model: "flux",
          overlay_text: overlayEnabled ? overlayText : null,
        }),
      });
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore sconosciuto";
      setResult({ status: "error", message: msg });
    } finally {
      setGenerating(false);
    }
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
            <ImagePlus className="w-5 h-5 text-white" />
          </div>
          Content Creator
        </h1>
        <p className="text-gray-400 mt-1">
          Genera immagini e video per le tue campagne con AI
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-2 border-b border-white/5 pb-px">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${
                active
                  ? "text-amber-400 border-b-2 border-amber-400 bg-amber-500/5"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ================================================================= */}
      {/* TAB: AI IMAGE GENERATOR                                           */}
      {/* ================================================================= */}
      {activeTab === "image" && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left: form (3 cols) */}
          <div className="lg:col-span-3 space-y-6">
            {/* Prompt templates */}
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-white">
                Template rapidi per settore
              </h3>
              <div className="flex flex-wrap gap-2">
                {PROMPT_TEMPLATES.map((t) => (
                  <button
                    key={t.label}
                    onClick={() => setPrompt(t.prompt)}
                    className="px-3 py-1.5 text-xs rounded-lg bg-white/5 text-gray-300 hover:bg-amber-500/10 hover:text-amber-400 border border-white/5 hover:border-amber-500/20 transition-all"
                  >
                    <span className="mr-1.5">{t.emoji}</span>
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Prompt area */}
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5 space-y-4">
              <label className="block text-sm font-semibold text-white">
                Descrivi l&apos;immagine
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder="Descrivi l'immagine per il tuo annuncio..."
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/40 resize-none"
              />

              {/* Format & Style row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">
                    Formato
                  </label>
                  <div className="relative">
                    <select
                      value={format}
                      onChange={(e) => setFormat(e.target.value)}
                      className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40 cursor-pointer"
                    >
                      {IMAGE_FORMATS.map((f) => (
                        <option key={f.value} value={f.value} className="bg-[#1a1a2e]">
                          {f.label} ({f.size})
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">
                    Stile
                  </label>
                  <div className="relative">
                    <select
                      value={style}
                      onChange={(e) => setStyle(e.target.value)}
                      className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/40 cursor-pointer"
                    >
                      {IMAGE_STYLES.map((s) => (
                        <option key={s.value} value={s.value} className="bg-[#1a1a2e]">
                          {s.label}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                  </div>
                </div>
              </div>

              {/* Overlay toggle */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setOverlayEnabled(!overlayEnabled)}
                  className={`relative w-10 h-5 rounded-full transition-colors ${
                    overlayEnabled ? "bg-amber-500" : "bg-white/10"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      overlayEnabled ? "translate-x-5" : ""
                    }`}
                  />
                </button>
                <span className="text-sm text-gray-300">
                  Aggiungi testo overlay
                </span>
              </div>
              {overlayEnabled && (
                <input
                  type="text"
                  value={overlayText}
                  onChange={(e) => setOverlayText(e.target.value)}
                  placeholder="Headline da sovrapporre all'immagine..."
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40"
                />
              )}

              {/* Generate button */}
              <button
                onClick={handleGenerate}
                disabled={generating || !prompt.trim()}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 text-white font-semibold text-sm hover:from-amber-400 hover:to-orange-500 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {generating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {generating ? "Generazione in corso..." : "Genera Immagine"}
              </button>
            </div>
          </div>

          {/* Right: preview (2 cols) */}
          <div className="lg:col-span-2">
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5 sticky top-8">
              <h3 className="text-sm font-semibold text-white mb-4">
                Anteprima
              </h3>

              {/* Result / Empty state */}
              {result ? (
                <div className="space-y-4">
                  {result.image_url ? (
                    <>
                      <img
                        src={result.image_url}
                        alt="Generated"
                        className="w-full rounded-lg border border-white/10"
                      />
                      <div className="flex gap-2">
                        <button className="flex-1 py-2 rounded-lg bg-white/5 text-gray-300 text-xs font-medium hover:bg-white/10 transition-colors flex items-center justify-center gap-1.5">
                          <Download className="w-3.5 h-3.5" />
                          Scarica
                        </button>
                        <button className="flex-1 py-2 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-medium hover:bg-amber-500/20 transition-colors flex items-center justify-center gap-1.5">
                          <Wand2 className="w-3.5 h-3.5" />
                          Genera Variante
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="rounded-lg border border-white/10 bg-white/[0.02] p-6 text-center space-y-3">
                      <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
                      <p className="text-sm text-gray-300">{result.message}</p>
                      {result.setup_url && (
                        <a
                          href={result.setup_url}
                          className="inline-flex items-center gap-1.5 text-xs text-amber-400 hover:text-amber-300 transition-colors"
                        >
                          <Settings className="w-3.5 h-3.5" />
                          Vai al Setup
                        </a>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="aspect-square rounded-lg border-2 border-dashed border-white/10 flex flex-col items-center justify-center text-center p-6 space-y-3">
                  <div className="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center">
                    <Image className="w-7 h-7 text-gray-600" />
                  </div>
                  <p className="text-sm text-gray-500">
                    L&apos;anteprima apparira qui dopo la generazione
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ================================================================= */}
      {/* TAB: VIDEO CREATOR                                                */}
      {/* ================================================================= */}
      {activeTab === "video" && (
        <div className="space-y-8">
          {/* Remotion section */}
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Play className="w-5 h-5 text-amber-400" />
                  Remotion — Video Integrato
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  Crea video ads direttamente dalla piattaforma con Remotion
                </p>
              </div>
              <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Integrato
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {VIDEO_TEMPLATES.map((t) => (
                <button
                  key={t.value}
                  onClick={() => setVideoTemplate(t.value)}
                  className={`p-4 rounded-lg border text-sm font-medium transition-all text-center ${
                    videoTemplate === t.value
                      ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
                      : "border-white/5 bg-white/[0.02] text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className="bg-black/30 rounded-lg border border-white/5 aspect-video flex items-center justify-center">
              <div className="text-center space-y-3">
                <div className="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mx-auto">
                  <Video className="w-7 h-7 text-gray-600" />
                </div>
                <p className="text-sm text-gray-500">
                  Player Remotion — In fase di integrazione
                </p>
                <p className="text-xs text-gray-600">
                  Template selezionato:{" "}
                  <span className="text-gray-400">
                    {VIDEO_TEMPLATES.find((t) => t.value === videoTemplate)?.label}
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* External tools */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">
              Strumenti Video Esterni
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {EXTERNAL_TOOLS.map((tool) => (
                <div
                  key={tool.name}
                  className="bg-white/[0.02] border border-white/5 rounded-xl p-5 space-y-3 hover:border-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <h4 className="font-semibold text-white">{tool.name}</h4>
                    <span
                      className={`px-2 py-0.5 text-[10px] font-medium rounded-full ${tool.badgeColor} border border-white/5`}
                    >
                      {tool.badge}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">{tool.description}</p>
                  {tool.external ? (
                    <a
                      href={tool.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/5 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
                    >
                      {tool.buttonLabel}
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  ) : (
                    <a
                      href={tool.internalUrl}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber-500/10 text-sm text-amber-400 hover:bg-amber-500/20 transition-colors"
                    >
                      <Settings className="w-3.5 h-3.5" />
                      {tool.buttonLabel}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ================================================================= */}
      {/* TAB: CREATIVE LIBRARY                                             */}
      {/* ================================================================= */}
      {activeTab === "library" && (
        <div className="bg-white/[0.02] border border-white/5 rounded-xl p-10 flex flex-col items-center justify-center text-center space-y-4 min-h-[400px]">
          <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
            <FolderOpen className="w-8 h-8 text-gray-600" />
          </div>
          <h3 className="text-lg font-semibold text-white">
            Nessun contenuto creativo
          </h3>
          <p className="text-sm text-gray-400 max-w-md">
            I contenuti generati o caricati appariranno qui. Usa il Generatore
            Immagini o il Video Creator per creare il tuo primo contenuto.
          </p>
          <button
            onClick={() => setActiveTab("image")}
            className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 text-white text-sm font-semibold hover:from-amber-400 hover:to-orange-500 transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Genera il tuo primo contenuto
          </button>
        </div>
      )}
    </div>
  );
}
