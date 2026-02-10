"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeftIcon,
  EyeIcon,
  PaperAirplaneIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  PhotoIcon,
  VideoCameraIcon,
  CodeBracketIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { getSite, updateSite, refineWebsite, deploySite, Site } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import EquipePromo from "@/components/EquipePromo";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const QUICK_ACTIONS = [
  "Cambia la combinazione di colori",
  "Aggiungi una nuova sezione",
  "Modifica i testi del sito",
  "Migliora il design mobile",
  "Cambia il font del sito",
  "Aggiungi animazioni",
];

export default function Editor() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const siteId = params.id as string;

  const [site, setSite] = useState<Site | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewMode, setPreviewMode] = useState<"desktop" | "mobile">("desktop");
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishedUrl, setPublishedUrl] = useState<string | null>(null);

  // Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isRefining, setIsRefining] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Attachment popover state
  const [activePopover, setActivePopover] = useState<"photo" | "video" | "embed" | null>(null);
  const [photoUrl, setPhotoUrl] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [embedCode, setEmbedCode] = useState("");
  const [videoError, setVideoError] = useState("");

  // Live HTML for preview (updated by chat refine)
  const [liveHtml, setLiveHtml] = useState<string>("");

  useEffect(() => {
    if (siteId) {
      loadSite();
    }
  }, [siteId]);

  useEffect(() => {
    if (site?.html_content) {
      setLiveHtml(site.html_content);
    }
    if (site?.domain) {
      setPublishedUrl(site.domain);
    }
  }, [site?.html_content, site?.domain]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadSite = async () => {
    try {
      setLoading(true);
      const data = await getSite(Number(siteId));
      setSite(data);
    } catch (error: any) {
      toast.error(error.message || "Errore nel caricamento sito");
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!site) return;

    try {
      setIsPublishing(true);
      const result = await deploySite(site.id);
      if (result.success && result.url) {
        setPublishedUrl(result.url);
        toast.success("Sito pubblicato su Vercel!");
      }
      loadSite();
    } catch (error: any) {
      if (error.isQuotaError || error.quota?.upgrade_required) {
        toast.error("Passa al piano Base o Premium per pubblicare il sito.");
      } else {
        toast.error(error.message || "Errore nella pubblicazione");
      }
    } finally {
      setIsPublishing(false);
    }
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || chatInput.trim();
    if (!text || !site || isRefining) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setIsRefining(true);

    try {
      const result = await refineWebsite({
        site_id: site.id,
        message: text,
      });

      if (result.success && result.html_content) {
        setLiveHtml(result.html_content);
        setSite((prev) => prev ? { ...prev, html_content: result.html_content! } : prev);

        const aiMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Modifica applicata con successo! (${Math.round((result.generation_time_ms || 0) / 1000)}s)`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      }
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Errore: ${error.message || "Impossibile applicare la modifica"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      toast.error(error.message || "Errore durante la modifica");
    } finally {
      setIsRefining(false);
    }
  };

  const validateVideoUrl = (url: string): boolean => {
    return /(?:youtube\.com\/watch\?v=|youtu\.be\/|vimeo\.com\/\d+)/.test(url);
  };

  const appendToChat = (text: string) => {
    setChatInput((prev) => (prev ? prev + "\n" + text : text));
    textareaRef.current?.focus();
  };

  const handlePhotoUrlSubmit = () => {
    if (!photoUrl.trim()) return;
    appendToChat(`[Inserisci questa immagine: ${photoUrl.trim()}]`);
    setPhotoUrl("");
    setActivePopover(null);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Immagine troppo grande (max 5MB)");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      appendToChat(`[Inserisci questa immagine: ${dataUrl}]`);
      setActivePopover(null);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleVideoSubmit = () => {
    if (!videoUrl.trim()) return;
    if (!validateVideoUrl(videoUrl.trim())) {
      setVideoError("URL non valido. Usa un link YouTube o Vimeo.");
      return;
    }
    appendToChat(`[Inserisci video: ${videoUrl.trim()}]`);
    setVideoUrl("");
    setVideoError("");
    setActivePopover(null);
  };

  const handleEmbedSubmit = () => {
    if (!embedCode.trim()) return;
    appendToChat(`[Inserisci embed: ${embedCode.trim()}]`);
    setEmbedCode("");
    setActivePopover(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStatusBadge = () => {
    if (!site) return null;

    switch (site.status) {
      case "published":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/20 text-emerald-400 text-sm">
            <CheckCircleIcon className="w-4 h-4" />
            Online
          </span>
        );
      case "ready":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-400 text-sm">
            <SparklesIcon className="w-4 h-4" />
            Pronto
          </span>
        );
      case "generating":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-400 text-sm">
            <ArrowPathIcon className="w-4 h-4 animate-spin" />
            Generazione...
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-500/20 text-slate-400 text-sm">
            <ExclamationCircleIcon className="w-4 h-4" />
            Bozza
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!site) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white">
        <div className="text-center">
          <p className="text-slate-400">Sito non trovato</p>
          <Link href="/dashboard" className="text-blue-500 hover:underline mt-2 inline-block">
            Torna alla dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col">
      {/* Header */}
      <header className="h-16 bg-[#111] border-b border-white/5 sticky top-0 z-50 flex-shrink-0">
        <div className="h-full px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-semibold">{site.name}</h1>
              <p className="text-sm text-slate-400">{site.slug}.e-quipe.app</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 ml-4">
              {getStatusBadge()}
            </div>
          </div>

          {/* Center: Preview Controls */}
          <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setPreviewMode("desktop")}
              className={`p-2 rounded-md transition-all ${
                previewMode === "desktop"
                  ? "bg-white/10 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
              title="Desktop view"
            >
              <ComputerDesktopIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setPreviewMode("mobile")}
              className={`p-2 rounded-md transition-all ${
                previewMode === "mobile"
                  ? "bg-white/10 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
              title="Mobile view"
            >
              <DevicePhoneMobileIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {/* Chat Toggle */}
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                chatOpen
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:text-white hover:bg-white/5"
              }`}
              title="Modifica con AI"
            >
              <ChatBubbleLeftRightIcon className="w-4 h-4" />
              <span className="hidden md:inline">Chat AI</span>
            </button>

            {/* Publish */}
            {site.is_published || publishedUrl ? (
              <div className="flex items-center gap-2">
                <a
                  href={publishedUrl || site.domain || `https://${site.slug}.vercel.app`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                >
                  <EyeIcon className="w-4 h-4" />
                  Visita
                </a>
                <button
                  onClick={handlePublish}
                  disabled={isPublishing}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all disabled:opacity-50"
                  title="Aggiorna il deploy"
                >
                  {isPublishing ? (
                    <ArrowPathIcon className="w-4 h-4 animate-spin" />
                  ) : (
                    <ArrowPathIcon className="w-4 h-4" />
                  )}
                </button>
              </div>
            ) : (
              <button
                onClick={handlePublish}
                disabled={isPublishing || site.status !== "ready"}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all"
              >
                {isPublishing ? (
                  <>
                    <ArrowPathIcon className="w-4 h-4 animate-spin" />
                    Pubblicazione...
                  </>
                ) : (
                  <>
                    <PaperAirplaneIcon className="w-4 h-4" />
                    Pubblica
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Preview + Chat */}
      <main className="flex-1 flex overflow-hidden">
        {/* Preview Area */}
        <div className="flex-1 bg-[#0a0a0a] relative overflow-hidden flex flex-col p-4 md:p-8">
          {/* Grid Background */}
          <div
            className="absolute inset-0 opacity-20 pointer-events-none"
            style={{
              backgroundImage: `
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
              `,
              backgroundSize: "20px 20px",
            }}
          />

          {/* Iframe Container */}
          <div className="flex-1 flex items-center justify-center min-h-0">
            <div
              className={`relative bg-white rounded-lg shadow-2xl overflow-hidden transition-all duration-300 ${
                previewMode === "mobile"
                  ? "w-[375px] h-[812px]"
                  : "w-full max-w-6xl h-full max-h-[calc(100vh-120px)]"
              }`}
            >
              {liveHtml ? (
                <iframe
                  srcDoc={liveHtml}
                  className="w-full h-full border-0"
                  sandbox="allow-scripts"
                  title={`Preview - ${site.name}`}
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 bg-slate-900">
                  <SparklesIcon className="w-12 h-12 mb-4 opacity-50" />
                  <p className="text-lg font-medium">Nessun contenuto generato</p>
                  <p className="text-sm opacity-70 mt-1">
                    Il sito non &egrave; stato ancora generato dall&apos;AI
                  </p>
                  <Link
                    href="/dashboard/new"
                    className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm transition-colors"
                  >
                    Crea nuovo sito
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* e-quipe Studio upsell - shown when site is ready/published */}
          {(site.status === "ready" || site.status === "published") && (
            <div className="relative z-10 mt-4 max-w-3xl mx-auto w-full">
              <EquipePromo
                userEmail={user?.email}
                siteName={site.name}
                variant="bar"
              />
            </div>
          )}
        </div>

        {/* Chat Panel (Right Sidebar) */}
        {chatOpen && (
          <aside className="w-[380px] bg-[#111] border-l border-white/5 flex flex-col flex-shrink-0">
            {/* Chat Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SparklesIcon className="w-5 h-5 text-blue-400" />
                <h3 className="font-semibold">Modifica con AI</h3>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                className="p-1 hover:bg-white/5 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-5 h-5 text-slate-400" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <SparklesIcon className="w-10 h-10 text-blue-400/50 mx-auto mb-3" />
                  <p className="text-slate-400 text-sm mb-4">
                    Descrivi le modifiche che vuoi apportare al tuo sito
                  </p>

                  {/* Quick Actions */}
                  <div className="space-y-2">
                    {QUICK_ACTIONS.map((action) => (
                      <button
                        key={action}
                        onClick={() => handleSendMessage(action)}
                        disabled={isRefining}
                        className="w-full text-left px-3 py-2 text-sm text-slate-300 bg-white/5 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-br-md"
                        : "bg-white/5 text-slate-300 rounded-bl-md"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}

              {/* Loading indicator */}
              {isRefining && (
                <div className="flex justify-start">
                  <div className="bg-white/5 text-slate-400 px-4 py-3 rounded-2xl rounded-bl-md text-sm flex items-center gap-2">
                    <ArrowPathIcon className="w-4 h-4 animate-spin" />
                    Applicazione modifiche...
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-white/5">
              {/* Attachment Bar */}
              <div className="relative mb-2">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setActivePopover(activePopover === "photo" ? null : "photo")}
                    className={`p-1.5 rounded-md transition-colors ${
                      activePopover === "photo"
                        ? "bg-white/10 text-white"
                        : "text-slate-400 hover:text-white hover:bg-white/5"
                    }`}
                    title="Inserisci immagine"
                  >
                    <PhotoIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => { setActivePopover(activePopover === "video" ? null : "video"); setVideoError(""); }}
                    className={`p-1.5 rounded-md transition-colors ${
                      activePopover === "video"
                        ? "bg-white/10 text-white"
                        : "text-slate-400 hover:text-white hover:bg-white/5"
                    }`}
                    title="Inserisci video"
                  >
                    <VideoCameraIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setActivePopover(activePopover === "embed" ? null : "embed")}
                    className={`p-1.5 rounded-md transition-colors ${
                      activePopover === "embed"
                        ? "bg-white/10 text-white"
                        : "text-slate-400 hover:text-white hover:bg-white/5"
                    }`}
                    title="Inserisci embed"
                  >
                    <CodeBracketIcon className="w-4 h-4" />
                  </button>
                </div>

                {/* Photo Popover */}
                {activePopover === "photo" && (
                  <div className="absolute bottom-full left-0 mb-2 w-72 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">Inserisci immagine</span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">Incolla URL immagine</label>
                        <div className="flex gap-1.5">
                          <input
                            type="text"
                            value={photoUrl}
                            onChange={(e) => setPhotoUrl(e.target.value)}
                            onKeyDown={(e) => { if (e.key === "Enter") handlePhotoUrlSubmit(); }}
                            placeholder="https://..."
                            className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                          />
                          <button
                            onClick={handlePhotoUrlSubmit}
                            disabled={!photoUrl.trim()}
                            className="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-lg text-xs font-medium transition-colors"
                          >
                            OK
                          </button>
                        </div>
                      </div>
                      <div className="border-t border-white/5 pt-2">
                        <label className="text-xs text-slate-400 mb-1 block">Carica dal dispositivo</label>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="w-full py-1.5 bg-white/5 border border-white/10 border-dashed rounded-lg text-xs text-slate-400 hover:text-white hover:border-white/20 transition-colors"
                        >
                          Scegli file...
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Video Popover */}
                {activePopover === "video" && (
                  <div className="absolute bottom-full left-0 mb-2 w-72 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">Inserisci video</span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">Incolla link YouTube o Vimeo</label>
                      <div className="flex gap-1.5">
                        <input
                          type="text"
                          value={videoUrl}
                          onChange={(e) => { setVideoUrl(e.target.value); setVideoError(""); }}
                          onKeyDown={(e) => { if (e.key === "Enter") handleVideoSubmit(); }}
                          placeholder="https://youtube.com/watch?v=..."
                          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                        />
                        <button
                          onClick={handleVideoSubmit}
                          disabled={!videoUrl.trim()}
                          className="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-lg text-xs font-medium transition-colors"
                        >
                          OK
                        </button>
                      </div>
                      {videoError && (
                        <p className="text-xs text-red-400 mt-1">{videoError}</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Embed Popover */}
                {activePopover === "embed" && (
                  <div className="absolute bottom-full left-0 mb-2 w-80 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">Inserisci embed</span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">
                        Incolla il codice embed (iframe, script, etc.)
                      </label>
                      <textarea
                        value={embedCode}
                        onChange={(e) => setEmbedCode(e.target.value)}
                        placeholder={'<iframe src="..."></iframe>'}
                        rows={4}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 resize-none focus:outline-none focus:border-blue-500 font-mono"
                      />
                      <button
                        onClick={handleEmbedSubmit}
                        disabled={!embedCode.trim()}
                        className="mt-1.5 w-full py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-lg text-xs font-medium transition-colors"
                      >
                        Inserisci
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <textarea
                  ref={textareaRef}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Descrivi la modifica..."
                  disabled={isRefining}
                  rows={2}
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 resize-none focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!chatInput.trim() || isRefining}
                  className="self-end p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-colors"
                >
                  <PaperAirplaneIcon className="w-5 h-5" />
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Invio per inviare, Shift+Invio per nuova riga
              </p>
            </div>
          </aside>
        )}
      </main>
    </div>
  );
}
