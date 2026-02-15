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
  ArrowUturnLeftIcon,
  QuestionMarkCircleIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { getSite, updateSite, refineWebsite, deploySite, regenerateImages, Site } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import EquipePromo from "@/components/EquipePromo";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const QUICK_ACTIONS = {
  it: [
    "Cambia la combinazione di colori",
    "Aggiungi una nuova sezione",
    "Modifica i testi del sito",
    "Migliora il design mobile",
    "Cambia il font del sito",
    "Aggiungi animazioni",
  ],
  en: [
    "Change the color scheme",
    "Add a new section",
    "Edit the site texts",
    "Improve mobile design",
    "Change the site font",
    "Add animations",
  ],
};

const GUIDE_SUGGESTIONS = {
  it: [
    {
      icon: "\uD83C\uDFA8",
      title: "Migliora i colori",
      description: "Cambia la palette colori per dare un look piu' professionale",
      chatMessage: "Cambia la palette colori con colori piu' vivaci e professionali, usa un design da Awwwards",
    },
    {
      icon: "\u270D\uFE0F",
      title: "Riscrivi i testi",
      description: "Rendi i testi piu' accattivanti e persuasivi",
      chatMessage: "Riscrivi tutti i testi del sito con un tono piu' professionale e accattivante, evita frasi generiche",
    },
    {
      icon: "\u2795",
      title: "Aggiungi sezioni",
      description: "Aggiungi testimonials, gallery, FAQ e altro",
      chatMessage: "Aggiungi una sezione testimonials con 3 recensioni e una sezione FAQ con 5 domande frequenti",
    },
    {
      icon: "\u2728",
      title: "Perfeziona il design",
      description: "Migliora layout, spaziature e animazioni",
      chatMessage: "Migliora il design generale: aggiungi piu' spaziatura tra le sezioni, hover effects sulle card, e gradient di sfondo",
    },
  ],
  en: [
    {
      icon: "\uD83C\uDFA8",
      title: "Improve colors",
      description: "Change the color palette for a more professional look",
      chatMessage: "Change the color palette with more vibrant and professional colors, use an Awwwards-level design",
    },
    {
      icon: "\u270D\uFE0F",
      title: "Rewrite texts",
      description: "Make texts more engaging and persuasive",
      chatMessage: "Rewrite all site texts with a more professional and engaging tone, avoid generic phrases",
    },
    {
      icon: "\u2795",
      title: "Add sections",
      description: "Add testimonials, gallery, FAQ and more",
      chatMessage: "Add a testimonials section with 3 reviews and a FAQ section with 5 frequently asked questions",
    },
    {
      icon: "\u2728",
      title: "Perfect the design",
      description: "Improve layout, spacing and animations",
      chatMessage: "Improve the overall design: add more spacing between sections, hover effects on cards, and background gradients",
    },
  ],
};

export default function Editor() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { language } = useLanguage();
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

  // Undo history
  const [htmlHistory, setHtmlHistory] = useState<string[]>([]);
  const [isUndoing, setIsUndoing] = useState(false);

  // Guide panel state
  const [showGuidePanel, setShowGuidePanel] = useState(false);

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

  // Show guide panel on first visit when site is ready/generated
  useEffect(() => {
    if (site && (site.status === "ready" || site.status === "published") && liveHtml) {
      const seen = localStorage.getItem("editor-guide-seen");
      if (!seen) {
        setShowGuidePanel(true);
      }
    }
  }, [site?.status, liveHtml]);

  const handleGuideDismiss = () => {
    setShowGuidePanel(false);
    setChatOpen(true);
    localStorage.setItem("editor-guide-seen", "true");
  };

  const handleGuideSuggestionClick = (chatMessage: string) => {
    setShowGuidePanel(false);
    setChatOpen(true);
    localStorage.setItem("editor-guide-seen", "true");
    setChatInput(chatMessage);
    // Focus the textarea after a short delay to allow render
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  const loadSite = async () => {
    try {
      setLoading(true);
      const data = await getSite(Number(siteId));
      setSite(data);
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "Error loading site" : "Errore nel caricamento sito"));
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
        toast.success(language === "en" ? "Site published!" : "Sito pubblicato!");
      }
      loadSite();
    } catch (error: any) {
      if (error.isQuotaError || error.quota?.upgrade_required) {
        toast.error(language === "en" ? "Upgrade to Base or Premium plan to publish the site." : "Passa al piano Base o Premium per pubblicare il sito.");
      } else {
        toast.error(error.message || (language === "en" ? "Error publishing" : "Errore nella pubblicazione"));
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
        language,
      });

      if (result.success && result.html_content) {
        if (liveHtml) {
          setHtmlHistory((prev) => [...prev, liveHtml]);
        }
        setLiveHtml(result.html_content);
        setSite((prev) => prev ? { ...prev, html_content: result.html_content! } : prev);

        const aiMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: language === "en"
            ? `Edit applied successfully! (${Math.round((result.generation_time_ms || 0) / 1000)}s)`
            : `Modifica applicata con successo! (${Math.round((result.generation_time_ms || 0) / 1000)}s)`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      } else {
        // API returned 200 but success=false or no html_content
        const errorMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: result.error || (language === "en"
            ? "The edit did not produce results. Try again with a different request."
            : "La modifica non ha prodotto risultati. Riprova con una richiesta diversa."),
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: language === "en"
          ? `Error: ${error.message || "Could not apply the edit"}`
          : `Errore: ${error.message || "Impossibile applicare la modifica"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      toast.error(error.message || (language === "en" ? "Error during edit" : "Errore durante la modifica"));
    } finally {
      setIsRefining(false);
    }
  };

  const handleUndo = () => {
    if (htmlHistory.length === 0 || isUndoing) return;
    setIsUndoing(true);
    const previousHtml = htmlHistory[htmlHistory.length - 1];
    setHtmlHistory((prev) => prev.slice(0, -1));
    setLiveHtml(previousHtml);
    setSite((prev) => prev ? { ...prev, html_content: previousHtml } : prev);
    // Also save to backend
    if (site) {
      updateSite(site.id, { html_content: previousHtml } as any)
        .then(() => {
          toast.success(language === "en" ? "Edit undone" : "Modifica annullata");
        })
        .catch(() => {
          toast.error(language === "en" ? "Error during undo" : "Errore durante l'annullamento");
        })
        .finally(() => setIsUndoing(false));
    } else {
      setIsUndoing(false);
    }

    const undoMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "assistant",
      content: language === "en"
        ? "Edit undone. Previous version restored."
        : "Modifica annullata. Ripristinata la versione precedente.",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, undoMsg]);
  };

  // Image regeneration
  const [isRegeneratingImages, setIsRegeneratingImages] = useState(false);
  const [imageRegenSection, setImageRegenSection] = useState<string | null>(null);

  const SECTION_TYPES = ["hero", "about", "gallery", "services", "portfolio", "team", "contact"];

  const handleRegenerateImages = async (sectionType: string) => {
    if (!site || isRegeneratingImages) return;
    setIsRegeneratingImages(true);
    setImageRegenSection(sectionType);

    const loadingMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "assistant",
      content: language === "en"
        ? `Generating new images for "${sectionType}" section...`
        : `Generazione nuove immagini per la sezione "${sectionType}"...`,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, loadingMsg]);

    try {
      const result = await regenerateImages({
        site_id: site.id,
        section_type: sectionType,
      });

      const successMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: language === "en"
          ? `Generated ${result.count} new image(s) for "${sectionType}". Use the chat to insert them into specific sections, e.g.: "Replace the ${sectionType} image with ${result.images[0]}"`
          : `Generate ${result.count} nuove immagini per "${sectionType}". Usa la chat per inserirle nelle sezioni, es: "Sostituisci l'immagine ${sectionType} con ${result.images[0]}"`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMsg]);
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: language === "en"
          ? `Error generating images: ${error.message}`
          : `Errore nella generazione immagini: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
      toast.error(language === "en" ? "Error generating images" : "Errore generazione immagini");
    } finally {
      setIsRegeneratingImages(false);
      setImageRegenSection(null);
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
    appendToChat(language === "en"
      ? `[Insert this image: ${photoUrl.trim()}]`
      : `[Inserisci questa immagine: ${photoUrl.trim()}]`);
    setPhotoUrl("");
    setActivePopover(null);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      toast.error(language === "en" ? "Image too large (max 5MB)" : "Immagine troppo grande (max 5MB)");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      appendToChat(language === "en"
        ? `[Insert this image: ${dataUrl}]`
        : `[Inserisci questa immagine: ${dataUrl}]`);
      setActivePopover(null);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleVideoSubmit = () => {
    if (!videoUrl.trim()) return;
    if (!validateVideoUrl(videoUrl.trim())) {
      setVideoError(language === "en" ? "Invalid URL. Use a YouTube or Vimeo link." : "URL non valido. Usa un link YouTube o Vimeo.");
      return;
    }
    appendToChat(language === "en"
      ? `[Insert video: ${videoUrl.trim()}]`
      : `[Inserisci video: ${videoUrl.trim()}]`);
    setVideoUrl("");
    setVideoError("");
    setActivePopover(null);
  };

  const handleEmbedSubmit = () => {
    if (!embedCode.trim()) return;
    appendToChat(language === "en"
      ? `[Insert embed: ${embedCode.trim()}]`
      : `[Inserisci embed: ${embedCode.trim()}]`);
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
            {language === "en" ? "Online" : "Online"}
          </span>
        );
      case "ready":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-400 text-sm">
            <SparklesIcon className="w-4 h-4" />
            {language === "en" ? "Ready" : "Pronto"}
          </span>
        );
      case "generating":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-400 text-sm">
            <ArrowPathIcon className="w-4 h-4 animate-spin" />
            {language === "en" ? "Generating..." : "Generazione..."}
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-500/20 text-slate-400 text-sm">
            <ExclamationCircleIcon className="w-4 h-4" />
            {language === "en" ? "Draft" : "Bozza"}
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
          <p className="text-slate-400">{language === "en" ? "Site not found" : "Sito non trovato"}</p>
          <Link href="/dashboard" className="text-blue-500 hover:underline mt-2 inline-block">
            {language === "en" ? "Back to dashboard" : "Torna alla dashboard"}
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
              title={language === "en" ? "Desktop view" : "Vista desktop"}
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
              title={language === "en" ? "Mobile view" : "Vista mobile"}
            >
              <DevicePhoneMobileIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {/* Guide Help Button */}
            <button
              onClick={() => setShowGuidePanel(true)}
              className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              title={language === "en" ? "Guide" : "Guida"}
            >
              <QuestionMarkCircleIcon className="w-5 h-5" />
            </button>

            {/* Chat Toggle */}
            <button
              onClick={() => {
                if (showGuidePanel) {
                  setShowGuidePanel(false);
                }
                setChatOpen(!chatOpen);
              }}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                chatOpen && !showGuidePanel
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:text-white hover:bg-white/5"
              }`}
              title={language === "en" ? "Edit with AI" : "Modifica con AI"}
            >
              <ChatBubbleLeftRightIcon className="w-4 h-4" />
              <span className="hidden md:inline">{language === "en" ? "AI Chat" : "Chat AI"}</span>
            </button>

            {/* Publish */}
            {site.is_published || publishedUrl ? (
              <div className="flex items-center gap-2">
                <a
                  href={publishedUrl || site.domain || `https://${site.slug}.e-quipe.app`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                >
                  <EyeIcon className="w-4 h-4" />
                  {language === "en" ? "Visit" : "Visita"}
                </a>
                <button
                  onClick={handlePublish}
                  disabled={isPublishing}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all disabled:opacity-50"
                  title={language === "en" ? "Update deployment" : "Aggiorna il deploy"}
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
                    {language === "en" ? "Publishing..." : "Pubblicazione..."}
                  </>
                ) : (
                  <>
                    <PaperAirplaneIcon className="w-4 h-4" />
                    {language === "en" ? "Publish" : "Pubblica"}
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
                  <p className="text-lg font-medium">
                    {language === "en" ? "No content generated" : "Nessun contenuto generato"}
                  </p>
                  <p className="text-sm opacity-70 mt-1">
                    {language === "en"
                      ? "The site has not been generated by AI yet"
                      : "Il sito non è stato ancora generato dall'AI"}
                  </p>
                  <Link
                    href="/dashboard/new"
                    className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm transition-colors"
                  >
                    {language === "en" ? "Create new site" : "Crea nuovo sito"}
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

        {/* Right Sidebar: Guide Panel or Chat Panel */}
        {(chatOpen || showGuidePanel) && (
          <aside className="w-full sm:w-[380px] fixed sm:relative inset-0 sm:inset-auto z-50 sm:z-auto bg-[#0d0d12] border-l border-white/10 flex flex-col flex-shrink-0">
            {showGuidePanel ? (
              <>
                {/* Guide Panel Header */}
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <SparklesIcon className="w-5 h-5 text-blue-400" />
                    <h3 className="font-semibold">{language === "en" ? "Guide" : "Guida"}</h3>
                  </div>
                  <button
                    onClick={() => setShowGuidePanel(false)}
                    className="p-1 hover:bg-white/5 rounded-lg transition-colors"
                  >
                    <XMarkIcon className="w-5 h-5 text-slate-400" />
                  </button>
                </div>

                {/* Guide Panel Content */}
                <div className="flex-1 overflow-y-auto p-5 flex flex-col">
                  {/* Title Section */}
                  <div className="text-center mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mx-auto mb-4">
                      <SparklesIcon className="w-7 h-7 text-blue-400" />
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">
                      {language === "en" ? "Your site is ready!" : "Il tuo sito e' pronto!"}
                    </h2>
                    <p className="text-sm text-slate-400">
                      {language === "en"
                        ? "Use AI Chat to customize every aspect"
                        : "Usa la Chat AI per personalizzare ogni aspetto"}
                    </p>
                  </div>

                  {/* Suggestion Cards */}
                  <div className="space-y-3 flex-1">
                    {GUIDE_SUGGESTIONS[language as "it" | "en"].map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleGuideSuggestionClick(suggestion.chatMessage)}
                        className="w-full text-left rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 p-4 transition-all group"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0 mt-0.5">{suggestion.icon}</span>
                          <div>
                            <h4 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                              {suggestion.title}
                            </h4>
                            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                              {suggestion.description}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {/* Bottom CTA Button */}
                  <div className="mt-6 pt-4 border-t border-white/10">
                    <button
                      onClick={handleGuideDismiss}
                      className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all"
                    >
                      {language === "en" ? "Got it, let's start!" : "Ho capito, inizia!"}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
            {/* Chat Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SparklesIcon className="w-5 h-5 text-blue-400" />
                <h3 className="font-semibold">{language === "en" ? "Edit with AI" : "Modifica con AI"}</h3>
              </div>
              <div className="flex items-center gap-1">
                {htmlHistory.length > 0 && (
                  <button
                    onClick={handleUndo}
                    disabled={isUndoing || isRefining}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 rounded-lg transition-colors disabled:opacity-50"
                    title={language === "en" ? "Undo last edit" : "Annulla ultima modifica"}
                  >
                    <ArrowUturnLeftIcon className="w-3.5 h-3.5" />
                    {language === "en" ? "Undo" : "Annulla"}
                  </button>
                )}
                <button
                  onClick={() => setChatOpen(false)}
                  className="p-1 hover:bg-white/5 rounded-lg transition-colors"
                >
                  <XMarkIcon className="w-5 h-5 text-slate-400" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <SparklesIcon className="w-10 h-10 text-blue-400/50 mx-auto mb-3" />
                  <p className="text-slate-400 text-sm mb-4">
                    {language === "en"
                      ? "Describe the changes you want to make to your site"
                      : "Descrivi le modifiche che vuoi apportare al tuo sito"}
                  </p>

                  {/* Quick Actions */}
                  <div className="space-y-2">
                    {QUICK_ACTIONS[language as "it" | "en"].map((action) => (
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

                  {/* Image Regeneration */}
                  <div className="mt-6 pt-4 border-t border-white/5">
                    <p className="text-xs text-slate-500 mb-2 flex items-center gap-1.5">
                      <PhotoIcon className="w-3.5 h-3.5" />
                      {language === "en" ? "Regenerate section images" : "Rigenera immagini sezione"}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {SECTION_TYPES.map((section) => (
                        <button
                          key={section}
                          onClick={() => handleRegenerateImages(section)}
                          disabled={isRegeneratingImages || isRefining}
                          className={`px-2.5 py-1.5 text-xs rounded-lg border transition-colors disabled:opacity-50 ${
                            imageRegenSection === section
                              ? "bg-violet-500/20 border-violet-500/40 text-violet-300"
                              : "bg-white/5 border-white/10 text-slate-400 hover:text-white hover:border-white/20"
                          }`}
                        >
                          {imageRegenSection === section ? (
                            <span className="flex items-center gap-1">
                              <ArrowPathIcon className="w-3 h-3 animate-spin" />
                              {section}
                            </span>
                          ) : (
                            section
                          )}
                        </button>
                      ))}
                    </div>
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
                    {language === "en" ? "Applying changes..." : "Applicazione modifiche..."}
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
                    title={language === "en" ? "Insert image" : "Inserisci immagine"}
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
                    title={language === "en" ? "Insert video" : "Inserisci video"}
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
                    title={language === "en" ? "Insert embed" : "Inserisci embed"}
                  >
                    <CodeBracketIcon className="w-4 h-4" />
                  </button>
                </div>

                {/* Photo Popover */}
                {activePopover === "photo" && (
                  <div className="absolute bottom-full left-0 mb-2 w-72 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">
                        {language === "en" ? "Insert image" : "Inserisci immagine"}
                      </span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="space-y-2">
                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">
                          {language === "en" ? "Paste image URL" : "Incolla URL immagine"}
                        </label>
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
                        <label className="text-xs text-slate-400 mb-1 block">
                          {language === "en" ? "Upload from device" : "Carica dal dispositivo"}
                        </label>
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
                          {language === "en" ? "Choose file..." : "Scegli file..."}
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Video Popover */}
                {activePopover === "video" && (
                  <div className="absolute bottom-full left-0 mb-2 w-72 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">
                        {language === "en" ? "Insert video" : "Inserisci video"}
                      </span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">
                        {language === "en" ? "Paste YouTube or Vimeo link" : "Incolla link YouTube o Vimeo"}
                      </label>
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
                  <div className="absolute bottom-full left-0 mb-2 w-[calc(100%-0.5rem)] max-w-80 bg-[#1a1a1a] border border-white/10 rounded-xl p-3 shadow-xl z-10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-300">
                        {language === "en" ? "Insert embed" : "Inserisci embed"}
                      </span>
                      <button onClick={() => setActivePopover(null)} className="text-slate-500 hover:text-white">
                        <XMarkIcon className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 mb-1 block">
                        {language === "en"
                          ? "Paste embed code (iframe, script, etc.)"
                          : "Incolla il codice embed (iframe, script, etc.)"}
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
                        {language === "en" ? "Insert" : "Inserisci"}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-end gap-2">
                <textarea
                  ref={textareaRef}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={language === "en" ? "Describe the edit..." : "Descrivi la modifica..."}
                  disabled={isRefining}
                  rows={2}
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 resize-none focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!chatInput.trim() || isRefining}
                  className="flex-shrink-0 p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl transition-colors mb-[1px]"
                >
                  <PaperAirplaneIcon className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                {language === "en"
                  ? "Enter to send, Shift+Enter for new line"
                  : "Invio per inviare, Shift+Invio per nuova riga"}
              </p>
            </div>
              </>
            )}
          </aside>
        )}
      </main>
    </div>
  );
}
