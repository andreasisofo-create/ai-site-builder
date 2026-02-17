"use client";

import { useState, useCallback } from "react";
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
  Copy,
  Check,
  Wand2,
  ImagePlus,
  RefreshCw,
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
const ASPECT_RATIOS = [
  { value: "1:1", label: "Feed Instagram 1:1", desc: "1080 x 1080" },
  { value: "9:16", label: "Stories / Reels 9:16", desc: "1080 x 1920" },
  { value: "16:9", label: "YouTube Thumbnail 16:9", desc: "1920 x 1080" },
  { value: "4:3", label: "Display 4:3", desc: "1440 x 1080" },
  { value: "4:5", label: "Portrait 4:5", desc: "1080 x 1350" },
  { value: "3:2", label: "Landscape 3:2", desc: "1620 x 1080" },
];

const STYLE_PRESETS = [
  {
    id: "food",
    emoji: "\uD83C\uDF55",
    label: "Food Photography",
    suffix:
      "high-resolution food photography, warm lighting, overhead shot, restaurant table setting, shallow depth of field",
  },
  {
    id: "saas",
    emoji: "\uD83D\uDCBB",
    label: "SaaS / Tech",
    suffix:
      "clean minimal UI screenshot on laptop, gradient background, modern tech aesthetic, soft shadows",
  },
  {
    id: "fitness",
    emoji: "\uD83D\uDCAA",
    label: "Fitness",
    suffix:
      "dramatic gym lighting, athlete in action, high contrast, motivational energy",
  },
  {
    id: "realestate",
    emoji: "\uD83C\uDFE0",
    label: "Immobiliare",
    suffix:
      "bright interior photography, natural light, wide angle lens, modern design",
  },
  {
    id: "beauty",
    emoji: "\uD83D\uDC88",
    label: "Beauty / Wellness",
    suffix:
      "soft pastel tones, spa atmosphere, clean and elegant, natural beauty",
  },
  {
    id: "ecommerce",
    emoji: "\uD83D\uDCE6",
    label: "E-commerce",
    suffix:
      "product photography, white background, studio lighting, professional shot",
  },
];

const VIDEO_STYLES = [
  { value: "cinematografico", label: "Cinematografico" },
  { value: "social_ugc", label: "Social / UGC" },
  { value: "product_demo", label: "Product Demo" },
  { value: "testimonial", label: "Testimonial" },
];

const VIDEO_DURATIONS = [
  { value: 5, label: "5 secondi" },
  { value: 10, label: "10 secondi" },
  { value: 15, label: "15 secondi" },
];

const EXTERNAL_VIDEO_TOOLS = [
  {
    name: "Seedance 2.0",
    url: "https://wavespeed.ai",
    description:
      "Video multimodali, lip-sync, template creativi. Incolla il prompt generato sopra.",
    badge: "Consigliato per Video Ads",
    badgeColor: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  },
  {
    name: "Higgsfield AI",
    url: "https://higgsfield.ai",
    description: "Video cinematografici, avatar AI parlanti, effetti premium.",
    badge: "Cinematografico",
    badgeColor: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  },
  {
    name: "RunwayML",
    url: "https://runwayml.com",
    description: "Gen-3 Alpha, video AI professionali di alta qualita.",
    badge: "Professionale",
    badgeColor: "text-blue-400 bg-blue-500/10 border-blue-500/20",
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
// Generated image type
// ---------------------------------------------------------------------------
interface GeneratedImage {
  dataUrl: string;
  prompt: string;
  aspectRatio: string;
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ContentCreatorPage() {
  const [activeTab, setActiveTab] = useState<Tab>("image");

  // ---- Image generator state ----
  const [prompt, setPrompt] = useState("");
  const [aspectRatio, setAspectRatio] = useState("1:1");
  const [activeStyle, setActiveStyle] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<{
    dataUrl: string;
    mimeType: string;
  } | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);

  // ---- Video prompt generator state ----
  const [videoDescription, setVideoDescription] = useState("");
  const [videoStyle, setVideoStyle] = useState("cinematografico");
  const [videoDuration, setVideoDuration] = useState(10);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [generatedVideoPrompt, setGeneratedVideoPrompt] = useState<string | null>(null);
  const [videoCopied, setVideoCopied] = useState(false);

  // ---- Library (session) ----
  const [library, setLibrary] = useState<GeneratedImage[]>([]);

  // ---- Clipboard ----
  const [promptCopied, setPromptCopied] = useState(false);

  // =========================================================================
  // Image Generation (Gemini)
  // =========================================================================
  const handleGenerateImage = useCallback(async () => {
    if (!prompt.trim()) return;
    setGenerating(true);
    setGeneratedImage(null);
    setImageError(null);

    const styleSuffix =
      activeStyle
        ? STYLE_PRESETS.find((s) => s.id === activeStyle)?.suffix || ""
        : "";

    try {
      const data = await adminFetch("/api/ads/generate-image-gemini", {
        method: "POST",
        body: JSON.stringify({
          prompt: prompt.trim(),
          aspect_ratio: aspectRatio,
          style_suffix: styleSuffix,
        }),
      });

      if (data.success && data.image_data) {
        const dataUrl = `data:${data.mime_type};base64,${data.image_data}`;
        setGeneratedImage({ dataUrl, mimeType: data.mime_type });
        // Add to session library
        setLibrary((prev) => [
          {
            dataUrl,
            prompt: prompt.trim(),
            aspectRatio,
            timestamp: Date.now(),
          },
          ...prev,
        ]);
      } else {
        setImageError(data.error || "Errore nella generazione.");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore sconosciuto";
      setImageError(msg);
    } finally {
      setGenerating(false);
    }
  }, [prompt, aspectRatio, activeStyle]);

  // =========================================================================
  // Download image
  // =========================================================================
  const handleDownload = useCallback(() => {
    if (!generatedImage) return;
    const ext = generatedImage.mimeType.includes("png") ? "png" : "jpg";
    const a = document.createElement("a");
    a.href = generatedImage.dataUrl;
    a.download = `gemini-image-${Date.now()}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [generatedImage]);

  // =========================================================================
  // Copy prompt
  // =========================================================================
  const handleCopyPrompt = useCallback(
    (text: string, setCopied: (v: boolean) => void) => {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    },
    []
  );

  // =========================================================================
  // Video Prompt Generation
  // =========================================================================
  const handleGenerateVideoPrompt = useCallback(async () => {
    if (!videoDescription.trim()) return;
    setGeneratingVideo(true);
    setGeneratedVideoPrompt(null);
    try {
      const data = await adminFetch("/api/ads/generate-video-prompt", {
        method: "POST",
        body: JSON.stringify({
          description: videoDescription.trim(),
          style: videoStyle,
          duration: videoDuration,
        }),
      });
      if (data.success && data.prompt) {
        setGeneratedVideoPrompt(data.prompt);
      }
    } catch {
      setGeneratedVideoPrompt(
        "Errore nella generazione del prompt. Verifica la configurazione AI."
      );
    } finally {
      setGeneratingVideo(false);
    }
  }, [videoDescription, videoStyle, videoDuration]);

  // =========================================================================
  // Render
  // =========================================================================
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-orange-600 flex items-center justify-center">
            <ImagePlus className="w-5 h-5 text-white" />
          </div>
          Content Creator
        </h1>
        <p className="text-gray-400 mt-1">
          Genera immagini con Gemini AI e prompt video ottimizzati per Seedance
          2.0
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
                  ? "text-violet-400 border-b-2 border-violet-400 bg-violet-500/5"
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
      {/* TAB: GEMINI IMAGE GENERATOR                                       */}
      {/* ================================================================= */}
      {activeTab === "image" && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left: form (3 cols) */}
          <div className="lg:col-span-3 space-y-6">
            {/* Style presets */}
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-white">
                Preset di stile (arricchiscono il prompt)
              </h3>
              <div className="flex flex-wrap gap-2">
                {STYLE_PRESETS.map((s) => (
                  <button
                    key={s.id}
                    onClick={() =>
                      setActiveStyle(activeStyle === s.id ? null : s.id)
                    }
                    className={`px-3 py-1.5 text-xs rounded-lg border transition-all ${
                      activeStyle === s.id
                        ? "border-violet-500/30 bg-violet-500/10 text-violet-400"
                        : "border-white/5 bg-white/5 text-gray-300 hover:bg-violet-500/10 hover:text-violet-400 hover:border-violet-500/20"
                    }`}
                  >
                    <span className="mr-1.5">{s.emoji}</span>
                    {s.label}
                  </button>
                ))}
              </div>
              {activeStyle && (
                <p className="text-xs text-gray-500 italic">
                  +{" "}
                  {STYLE_PRESETS.find((s) => s.id === activeStyle)?.suffix}
                </p>
              )}
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
                placeholder="Descrivi la scena in modo narrativo: ambientazione, soggetto, illuminazione, atmosfera..."
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-500/40 resize-none"
              />

              {/* Aspect ratio selector */}
              <div>
                <label className="block text-xs text-gray-400 mb-1.5">
                  Formato
                </label>
                <div className="relative">
                  <select
                    value={aspectRatio}
                    onChange={(e) => setAspectRatio(e.target.value)}
                    className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/40 cursor-pointer"
                  >
                    {ASPECT_RATIOS.map((ar) => (
                      <option
                        key={ar.value}
                        value={ar.value}
                        className="bg-[#1a1a2e]"
                      >
                        {ar.label} ({ar.desc})
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                </div>
              </div>

              {/* Generate button */}
              <button
                onClick={handleGenerateImage}
                disabled={generating || !prompt.trim()}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-violet-500 to-orange-600 text-white font-semibold text-sm hover:from-violet-400 hover:to-orange-500 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {generating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {generating
                  ? "Generazione con Gemini..."
                  : "Genera con Gemini"}
              </button>
            </div>
          </div>

          {/* Right: preview (2 cols) */}
          <div className="lg:col-span-2">
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-5 sticky top-8">
              <h3 className="text-sm font-semibold text-white mb-4">
                Anteprima
              </h3>

              {imageError ? (
                <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-6 text-center space-y-2">
                  <p className="text-sm text-red-400">{imageError}</p>
                  <button
                    onClick={() => setImageError(null)}
                    className="text-xs text-gray-400 hover:text-white transition-colors"
                  >
                    Chiudi
                  </button>
                </div>
              ) : generatedImage ? (
                <div className="space-y-4">
                  <img
                    src={generatedImage.dataUrl}
                    alt="Generata con Gemini"
                    className="w-full rounded-lg border border-white/10"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleDownload}
                      className="flex-1 py-2 rounded-lg bg-white/5 text-gray-300 text-xs font-medium hover:bg-white/10 transition-colors flex items-center justify-center gap-1.5"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Scarica PNG
                    </button>
                    <button
                      onClick={handleGenerateImage}
                      disabled={generating}
                      className="flex-1 py-2 rounded-lg bg-violet-500/10 text-violet-400 text-xs font-medium hover:bg-violet-500/20 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-40"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Genera Variante
                    </button>
                  </div>
                  <button
                    onClick={() =>
                      handleCopyPrompt(prompt, setPromptCopied)
                    }
                    className="w-full py-2 rounded-lg bg-white/5 text-gray-400 text-xs font-medium hover:bg-white/10 transition-colors flex items-center justify-center gap-1.5"
                  >
                    {promptCopied ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                    {promptCopied ? "Copiato!" : "Copia Prompt"}
                  </button>
                </div>
              ) : (
                <div className="aspect-square rounded-lg border-2 border-dashed border-white/10 flex flex-col items-center justify-center text-center p-6 space-y-3">
                  <div className="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center">
                    <Image className="w-7 h-7 text-gray-600" />
                  </div>
                  <p className="text-sm text-gray-500">
                    L&apos;anteprima apparira qui dopo la generazione
                  </p>
                  <p className="text-xs text-gray-600">
                    Powered by Gemini 2.5 Flash
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
          {/* AI Prompt Generator */}
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Wand2 className="w-5 h-5 text-violet-400" />
                  AI Prompt Generator per Video
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  L&apos;AI scrive prompt ottimizzati per Seedance 2.0. Copia e
                  incolla su WaveSpeed AI.
                </p>
              </div>
              <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
                AI Integrato
              </span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-white mb-1.5">
                  Descrivi il video che vuoi creare
                </label>
                <textarea
                  value={videoDescription}
                  onChange={(e) => setVideoDescription(e.target.value)}
                  rows={3}
                  placeholder="Es: Un piatto di pasta viene servito in un ristorante elegante, con vapore che sale e luce calda..."
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/40 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">
                    Stile
                  </label>
                  <div className="relative">
                    <select
                      value={videoStyle}
                      onChange={(e) => setVideoStyle(e.target.value)}
                      className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/40 cursor-pointer"
                    >
                      {VIDEO_STYLES.map((s) => (
                        <option
                          key={s.value}
                          value={s.value}
                          className="bg-[#1a1a2e]"
                        >
                          {s.label}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1.5">
                    Durata
                  </label>
                  <div className="relative">
                    <select
                      value={videoDuration}
                      onChange={(e) =>
                        setVideoDuration(Number(e.target.value))
                      }
                      className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/40 cursor-pointer"
                    >
                      {VIDEO_DURATIONS.map((d) => (
                        <option
                          key={d.value}
                          value={d.value}
                          className="bg-[#1a1a2e]"
                        >
                          {d.label}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                  </div>
                </div>
              </div>

              <button
                onClick={handleGenerateVideoPrompt}
                disabled={generatingVideo || !videoDescription.trim()}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-violet-500 to-orange-600 text-white font-semibold text-sm hover:from-violet-400 hover:to-orange-500 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {generatingVideo ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {generatingVideo
                  ? "Generazione prompt..."
                  : "Genera Prompt Seedance"}
              </button>
            </div>

            {/* Generated prompt output */}
            {generatedVideoPrompt && (
              <div className="mt-4 space-y-3">
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wide">
                  Prompt generato
                </label>
                <div className="bg-black/30 border border-white/10 rounded-lg p-4">
                  <p className="text-sm text-white whitespace-pre-wrap font-mono leading-relaxed">
                    {generatedVideoPrompt}
                  </p>
                </div>
                <button
                  onClick={() =>
                    handleCopyPrompt(generatedVideoPrompt, setVideoCopied)
                  }
                  className="w-full py-2.5 rounded-lg bg-violet-500/10 text-violet-400 text-sm font-medium hover:bg-violet-500/20 transition-colors flex items-center justify-center gap-2"
                >
                  {videoCopied ? (
                    <Check className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                  {videoCopied
                    ? "Copiato negli appunti!"
                    : "Copia Prompt"}
                </button>
              </div>
            )}
          </div>

          {/* External video tools */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">
              Crea Video su Piattaforme Esterne
            </h3>
            <p className="text-sm text-gray-400 -mt-2">
              Incolla il prompt generato sopra in una di queste piattaforme.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {EXTERNAL_VIDEO_TOOLS.map((tool) => (
                <div
                  key={tool.name}
                  className="bg-white/[0.02] border border-white/5 rounded-xl p-5 space-y-3 hover:border-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <h4 className="font-semibold text-white">{tool.name}</h4>
                    <span
                      className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${tool.badgeColor}`}
                    >
                      {tool.badge}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">{tool.description}</p>
                  <a
                    href={tool.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/5 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    Apri {tool.name}
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
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
        <>
          {library.length === 0 ? (
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-10 flex flex-col items-center justify-center text-center space-y-4 min-h-[400px]">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
                <FolderOpen className="w-8 h-8 text-gray-600" />
              </div>
              <h3 className="text-lg font-semibold text-white">
                Nessun contenuto creativo
              </h3>
              <p className="text-sm text-gray-400 max-w-md">
                I contenuti generati appariranno qui. Usa il Generatore
                Immagini per creare il tuo primo contenuto.
              </p>
              <button
                onClick={() => setActiveTab("image")}
                className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-violet-500 to-orange-600 text-white text-sm font-semibold hover:from-violet-400 hover:to-orange-500 transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Genera il tuo primo contenuto
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">
                  Contenuti generati ({library.length})
                </h3>
                <span className="text-xs text-gray-500">
                  Sessione corrente
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {library.map((img) => (
                  <div
                    key={img.timestamp}
                    className="group bg-white/[0.02] border border-white/5 rounded-xl overflow-hidden hover:border-white/10 transition-colors"
                  >
                    <div className="aspect-square overflow-hidden">
                      <img
                        src={img.dataUrl}
                        alt={img.prompt}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    <div className="p-3 space-y-2">
                      <p className="text-xs text-gray-400 line-clamp-2">
                        {img.prompt}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-gray-500">
                          {img.aspectRatio}
                        </span>
                        <a
                          href={img.dataUrl}
                          download={`gemini-${img.timestamp}.png`}
                          className="text-xs text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1"
                        >
                          <Download className="w-3 h-3" />
                          Scarica
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
