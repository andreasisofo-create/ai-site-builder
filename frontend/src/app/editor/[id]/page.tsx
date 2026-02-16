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
import {
  getSite, updateSite, refineWebsite, deploySite, regenerateImages, Site,
  uploadMedia, getSiteImages, replaceImage, addVideo, SiteImage,
} from "@/lib/api";
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
    "Rigenera la sezione Hero con un design diverso",
    "Riscrivi tutti i testi con un tono piu' audace",
  ],
  en: [
    "Change the color scheme",
    "Add a new section",
    "Edit the site texts",
    "Improve mobile design",
    "Change the site font",
    "Add animations",
    "Regenerate the Hero section with a different design",
    "Rewrite all texts with a bolder tone",
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
  const rawId = params?.id;
  const siteId = Array.isArray(rawId) ? rawId[0] : (rawId as string);

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
  const [pendingPhotos, setPendingPhotos] = useState<string[]>([]);  // photo URLs waiting to be sent with next message

  // Live HTML for preview (updated by chat refine)
  const [liveHtml, setLiveHtml] = useState<string>("");

  // Undo history
  const [htmlHistory, setHtmlHistory] = useState<string[]>([]);
  const [isUndoing, setIsUndoing] = useState(false);

  // Guide panel state
  const [showGuidePanel, setShowGuidePanel] = useState(false);

  // Media panel state
  const [showMediaPanel, setShowMediaPanel] = useState(false);
  const [siteImages, setSiteImages] = useState<SiteImage[]>([]);
  const [loadingImages, setLoadingImages] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadedUrls, setUploadedUrls] = useState<string[]>([]);
  const [replacingImage, setReplacingImage] = useState<string | null>(null);
  const [mediaVideoUrl, setMediaVideoUrl] = useState("");
  const [mediaVideoError, setMediaVideoError] = useState("");
  const [mediaVideoSection, setMediaVideoSection] = useState("hero");
  const [addingVideo, setAddingVideo] = useState(false);
  const mediaFileInputRef = useRef<HTMLInputElement>(null);
  const replaceFileInputRef = useRef<HTMLInputElement>(null);
  const replacingImageRef = useRef<string | null>(null);

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

  // Show guide panel on first visit per site when site is ready/generated
  useEffect(() => {
    if (site && siteId && (site.status === "ready" || site.status === "published") && liveHtml) {
      try {
        const seen = localStorage.getItem(`editor-guide-${siteId}`);
        if (!seen) {
          setShowGuidePanel(true);
        }
      } catch {
        // localStorage may throw in private browsing mode
      }
    }
  }, [site?.status, liveHtml, siteId]);

  const handleGuideDismiss = () => {
    setShowGuidePanel(false);
    setChatOpen(true);
    try { localStorage.setItem(`editor-guide-${siteId}`, "true"); } catch {}
  };

  const handleGuideSuggestionClick = (chatMessage: string) => {
    setShowGuidePanel(false);
    setChatOpen(true);
    try { localStorage.setItem("editor-guide-seen", "true"); } catch {}
    setChatInput(chatMessage);
    // Focus the textarea after a short delay to allow render
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  // Media panel handlers
  const loadSiteImages = async () => {
    if (!site) return;
    setLoadingImages(true);
    try {
      const result = await getSiteImages(site.id);
      setSiteImages(result.images || []);
    } catch {
      toast.error(language === "en" ? "Error loading images" : "Errore caricamento immagini");
    } finally {
      setLoadingImages(false);
    }
  };

  const openMediaPanel = () => {
    setShowMediaPanel(true);
    setShowGuidePanel(false);
    setChatOpen(false);
    loadSiteImages();
  };

  const handleMediaUpload = async (file: File) => {
    if (!site) return;
    if (file.size > 10 * 1024 * 1024) {
      toast.error(language === "en" ? "File too large (max 10MB)" : "File troppo grande (max 10MB)");
      return;
    }
    setUploadingFile(true);
    try {
      const result = await uploadMedia(site.id, file);
      setUploadedUrls((prev) => [...prev, result.url]);
      toast.success(language === "en" ? "Image uploaded" : "Immagine caricata");
    } catch (err: any) {
      toast.error(err.message || (language === "en" ? "Upload error" : "Errore caricamento"));
    } finally {
      setUploadingFile(false);
    }
  };

  const handleReplaceImage = async (oldSrc: string, file: File) => {
    if (!site) return;
    setReplacingImage(oldSrc);
    try {
      const uploaded = await uploadMedia(site.id, file);
      if (liveHtml) {
        setHtmlHistory((prev) => [...prev, liveHtml]);
      }
      const result = await replaceImage(site.id, oldSrc, uploaded.url);
      setLiveHtml(result.html_content);
      setSite((prev) => prev ? { ...prev, html_content: result.html_content } : prev);
      toast.success(language === "en" ? "Image replaced" : "Immagine sostituita");
      loadSiteImages();
    } catch (err: any) {
      toast.error(err.message || (language === "en" ? "Replace error" : "Errore sostituzione"));
    } finally {
      setReplacingImage(null);
    }
  };

  const handleUseUploadedImage = async (uploadedUrl: string, targetImage: SiteImage) => {
    if (!site) return;
    setReplacingImage(targetImage.src);
    try {
      if (liveHtml) {
        setHtmlHistory((prev) => [...prev, liveHtml]);
      }
      const result = await replaceImage(site.id, targetImage.src, uploadedUrl);
      setLiveHtml(result.html_content);
      setSite((prev) => prev ? { ...prev, html_content: result.html_content } : prev);
      toast.success(language === "en" ? "Image replaced" : "Immagine sostituita");
      loadSiteImages();
    } catch (err: any) {
      toast.error(err.message || (language === "en" ? "Replace error" : "Errore sostituzione"));
    } finally {
      setReplacingImage(null);
    }
  };

  const handleAddVideo = async () => {
    if (!site || !mediaVideoUrl.trim()) return;
    if (!validateVideoUrl(mediaVideoUrl.trim())) {
      setMediaVideoError(language === "en" ? "Invalid URL. Use a YouTube or Vimeo link." : "URL non valido. Usa un link YouTube o Vimeo.");
      return;
    }
    setAddingVideo(true);
    try {
      if (liveHtml) {
        setHtmlHistory((prev) => [...prev, liveHtml]);
      }
      const result = await addVideo(site.id, mediaVideoUrl.trim(), mediaVideoSection);
      setLiveHtml(result.html_content);
      setSite((prev) => prev ? { ...prev, html_content: result.html_content } : prev);
      setMediaVideoUrl("");
      setMediaVideoError("");
      toast.success(language === "en" ? "Video added" : "Video aggiunto");
    } catch (err: any) {
      toast.error(err.message || (language === "en" ? "Error adding video" : "Errore aggiunta video"));
    } finally {
      setAddingVideo(false);
    }
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
    if ((!text && pendingPhotos.length === 0) || !site || isRefining) return;

    // Collect pending photos and clean message from old-style inline image markers
    const photosToSend = [...pendingPhotos];
    // Also extract any legacy inline image markers: [Inserisci questa immagine: URL] or [Insert this image: URL]
    const imgRegex = /\[(?:Inserisci questa immagine|Insert this image):\s*((?:data:image\/[^[\]]+|https?:\/\/[^[\]]+))\]/g;
    let cleanMessage = text;
    let match;
    while ((match = imgRegex.exec(text)) !== null) {
      if (match[1] && !photosToSend.includes(match[1])) {
        photosToSend.push(match[1]);
      }
    }
    cleanMessage = text.replace(imgRegex, "").trim();
    // If message became empty after stripping image markers, add default instruction
    if (!cleanMessage && photosToSend.length > 0) {
      cleanMessage = language === "en"
        ? "Insert the attached image(s) into the site in an appropriate position"
        : "Inserisci le immagini allegate nel sito in una posizione appropriata";
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,  // Show original text to user (with placeholders)
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setPendingPhotos([]);  // Clear pending photos after sending
    setIsRefining(true);

    try {
      const result = await refineWebsite({
        site_id: site.id,
        message: cleanMessage || text,
        language,
        photo_urls: photosToSend.length > 0 ? photosToSend : undefined,
      });

      if (result.success && result.html_content) {
        if (liveHtml) {
          setHtmlHistory((prev) => [...prev, liveHtml]);
        }
        setLiveHtml(result.html_content);
        setSite((prev) => prev ? { ...prev, html_content: result.html_content! } : prev);

        const timeStr = `${Math.round((result.generation_time_ms || 0) / 1000)}s`;
        const strategyLabels: Record<string, string> = {
          css_vars: "stile",
          text: "testo",
          section: "sezione",
          structural: "struttura",
        };
        const strategyLabel = result.strategy ? strategyLabels[result.strategy] || result.strategy : "";
        const aiMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: language === "en"
            ? `Edit applied successfully! (${timeStr}${strategyLabel ? `, ${strategyLabel}` : ""})`
            : `Modifica applicata con successo! (${timeStr}${strategyLabel ? `, ${strategyLabel}` : ""})`,
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
    setPendingPhotos(prev => [...prev, photoUrl.trim()]);
    appendToChat(language === "en"
      ? `[Insert image ${pendingPhotos.length + 1}]`
      : `[Inserisci immagine ${pendingPhotos.length + 1}]`);
    setPhotoUrl("");
    setActivePopover(null);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !site) return;
    if (file.size > 5 * 1024 * 1024) {
      toast.error(language === "en" ? "Image too large (max 5MB)" : "Immagine troppo grande (max 5MB)");
      return;
    }
    // Upload via CDN to get a short server URL (instead of embedding base64)
    const toastId = toast.loading(language === "en" ? "Uploading image..." : "Caricamento immagine...");
    try {
      const { url } = await uploadMedia(site.id, file);
      toast.dismiss(toastId);
      toast.success(language === "en" ? "Image uploaded" : "Immagine caricata");
      setPendingPhotos(prev => [...prev, url]);
      appendToChat(language === "en"
        ? `[Insert uploaded image ${pendingPhotos.length + 1}]`
        : `[Inserisci immagine caricata ${pendingPhotos.length + 1}]`);
      setActivePopover(null);
    } catch {
      toast.dismiss(toastId);
      toast.error(language === "en" ? "Upload failed, try again" : "Caricamento fallito, riprova");
    }
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

            {/* Media Toggle */}
            <button
              onClick={openMediaPanel}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                showMediaPanel
                  ? "bg-emerald-600 text-white"
                  : "text-slate-300 hover:text-white hover:bg-white/5"
              }`}
              title="Media"
            >
              <PhotoIcon className="w-4 h-4" />
              <span className="hidden md:inline">Media</span>
            </button>

            {/* Chat Toggle */}
            <button
              onClick={() => {
                if (showGuidePanel) {
                  setShowGuidePanel(false);
                }
                setShowMediaPanel(false);
                setChatOpen(!chatOpen);
              }}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all ${
                chatOpen && !showGuidePanel && !showMediaPanel
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

      {/* Main Content - Sidebar (left) + Preview */}
      <main className="flex-1 flex overflow-hidden">
        {/* Preview Area — order-2 so sidebar (order-1) appears first/left */}
        <div className="flex-1 bg-[#0a0a0a] relative overflow-hidden flex flex-col p-4 md:p-8 order-2">
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
                  srcDoc={liveHtml
                    .replace(
                      '</head>',
                      `<style>
                        /* Editor preview overrides: force all content visible */
                        [data-animate] { opacity: 1 !important; transform: none !important; }
                        footer { position: static !important; }
                        section::after { display: none !important; }
                        body::after { display: none !important; }
                        .cursor-glow { display: none !important; }
                      </style></head>`
                    )
                    .replace(
                      '</body>',
                      `<script>
                        document.addEventListener('click', function(e) {
                          var a = e.target.closest('a');
                          if (!a) return;
                          var href = a.getAttribute('href');
                          if (href && href.startsWith('#')) {
                            e.preventDefault();
                            var target = document.querySelector(href);
                            if (target) target.scrollIntoView({ behavior: 'smooth' });
                          } else if (href && !href.startsWith('#')) {
                            e.preventDefault();
                          }
                        });
                      </script></body>`
                    )
                  }
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

        {/* Left Sidebar: Guide Panel, Chat Panel, or Media Panel */}
        {(chatOpen || showGuidePanel || showMediaPanel) && (
          <aside className="w-full sm:w-[380px] fixed sm:relative inset-0 sm:inset-auto z-50 sm:z-auto bg-[#0d0d12] border-r border-white/10 flex flex-col flex-shrink-0 order-1">
            {showMediaPanel ? (
              <>
                {/* Media Panel Header */}
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <PhotoIcon className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-semibold">Media</h3>
                  </div>
                  <button
                    onClick={() => setShowMediaPanel(false)}
                    className="p-1 hover:bg-white/5 rounded-lg transition-colors"
                  >
                    <XMarkIcon className="w-5 h-5 text-slate-400" />
                  </button>
                </div>

                {/* Media Panel Content */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6">

                  {/* Section A: Site Images */}
                  <div>
                    <h4 className="text-sm font-semibold text-white/90 mb-3 flex items-center gap-2">
                      <PhotoIcon className="w-4 h-4 text-emerald-400" />
                      {language === "en" ? "Site Images" : "Immagini del sito"}
                    </h4>
                    {loadingImages ? (
                      <div className="flex items-center justify-center py-8">
                        <ArrowPathIcon className="w-5 h-5 animate-spin text-slate-400" />
                      </div>
                    ) : siteImages.length === 0 ? (
                      <p className="text-xs text-slate-500 text-center py-4">
                        {language === "en" ? "No images found in the site" : "Nessuna immagine trovata nel sito"}
                      </p>
                    ) : (
                      <div className="space-y-2">
                        {/* Group by section */}
                        {Object.entries(
                          siteImages.reduce<Record<string, SiteImage[]>>((acc, img) => {
                            const key = img.section || "other";
                            if (!acc[key]) acc[key] = [];
                            acc[key].push(img);
                            return acc;
                          }, {})
                        ).map(([section, images]) => (
                          <div key={section}>
                            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1.5">{section}</p>
                            <div className="grid grid-cols-2 gap-2">
                              {images.map((img, idx) => (
                                <div
                                  key={`${section}-${idx}`}
                                  className="group relative bg-white/5 rounded-lg overflow-hidden border border-white/10 hover:border-white/20 transition-colors"
                                >
                                  <img
                                    src={img.src}
                                    alt={img.alt || section}
                                    className="w-full h-20 object-cover"
                                    onError={(e) => { (e.target as HTMLImageElement).src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='80' fill='%23333'%3E%3Crect width='100' height='80'/%3E%3Ctext x='50%25' y='50%25' fill='%23666' text-anchor='middle' dy='.3em' font-size='10'%3EImg%3C/text%3E%3C/svg%3E"; }}
                                  />
                                  <div className="p-1.5">
                                    <p className="text-[10px] text-slate-400 truncate">{img.alt || `${section} #${img.index + 1}`}</p>
                                  </div>
                                  <button
                                    onClick={() => {
                                      replacingImageRef.current = img.src;
                                      setReplacingImage(img.src);
                                      replaceFileInputRef.current?.click();
                                    }}
                                    disabled={replacingImage === img.src}
                                    className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity"
                                  >
                                    {replacingImage === img.src ? (
                                      <ArrowPathIcon className="w-5 h-5 text-white animate-spin" />
                                    ) : (
                                      <span className="text-xs font-medium text-white bg-emerald-600 px-3 py-1.5 rounded-lg">
                                        {language === "en" ? "Replace" : "Sostituisci"}
                                      </span>
                                    )}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    {/* Hidden file input for replacing images */}
                    <input
                      ref={replaceFileInputRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        const target = replacingImageRef.current;
                        if (file && target) {
                          handleReplaceImage(target, file);
                        }
                        e.target.value = "";
                      }}
                    />
                  </div>

                  {/* Section B: Upload New Photos */}
                  <div>
                    <h4 className="text-sm font-semibold text-white/90 mb-3 flex items-center gap-2">
                      <ArrowPathIcon className="w-4 h-4 text-emerald-400" />
                      {language === "en" ? "Upload Photos" : "Carica foto"}
                    </h4>
                    <input
                      ref={mediaFileInputRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleMediaUpload(file);
                        e.target.value = "";
                      }}
                    />
                    <button
                      onClick={() => mediaFileInputRef.current?.click()}
                      disabled={uploadingFile}
                      className="w-full py-6 border-2 border-dashed border-white/10 hover:border-emerald-500/40 rounded-xl text-sm text-slate-400 hover:text-emerald-400 transition-colors disabled:opacity-50 flex flex-col items-center gap-2"
                    >
                      {uploadingFile ? (
                        <>
                          <ArrowPathIcon className="w-6 h-6 animate-spin" />
                          <span>{language === "en" ? "Uploading..." : "Caricamento..."}</span>
                        </>
                      ) : (
                        <>
                          <PhotoIcon className="w-6 h-6" />
                          <span>{language === "en" ? "Click to upload an image" : "Clicca per caricare un'immagine"}</span>
                          <span className="text-[10px] text-slate-500">Max 10MB - JPG, PNG, WebP</span>
                        </>
                      )}
                    </button>

                    {/* Uploaded Images Gallery */}
                    {uploadedUrls.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-slate-500 mb-2">
                          {language === "en" ? "Uploaded images" : "Immagini caricate"} ({uploadedUrls.length})
                        </p>
                        <div className="grid grid-cols-3 gap-2">
                          {uploadedUrls.map((url, idx) => (
                            <div key={idx} className="relative group">
                              <img
                                src={url}
                                alt={`Upload ${idx + 1}`}
                                className="w-full h-16 object-cover rounded-lg border border-white/10"
                              />
                              {/* Show "Use in..." on hover if there are site images to replace */}
                              {siteImages.length > 0 && (
                                <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                                  <select
                                    className="bg-[#111] text-xs text-white border border-white/20 rounded px-1.5 py-1 cursor-pointer max-w-[90%]"
                                    defaultValue=""
                                    onChange={(e) => {
                                      const targetIdx = parseInt(e.target.value);
                                      if (!isNaN(targetIdx) && siteImages[targetIdx]) {
                                        handleUseUploadedImage(url, siteImages[targetIdx]);
                                      }
                                      e.target.value = "";
                                    }}
                                  >
                                    <option value="" disabled>{language === "en" ? "Use in..." : "Usa in..."}</option>
                                    {siteImages.map((img, sIdx) => (
                                      <option key={sIdx} value={sIdx}>
                                        {img.section} #{img.index + 1}
                                      </option>
                                    ))}
                                  </select>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Section C: Add Video */}
                  <div>
                    <h4 className="text-sm font-semibold text-white/90 mb-3 flex items-center gap-2">
                      <VideoCameraIcon className="w-4 h-4 text-emerald-400" />
                      {language === "en" ? "Add Video" : "Aggiungi video"}
                    </h4>
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">
                          {language === "en" ? "YouTube or Vimeo URL" : "URL YouTube o Vimeo"}
                        </label>
                        <input
                          type="text"
                          value={mediaVideoUrl}
                          onChange={(e) => { setMediaVideoUrl(e.target.value); setMediaVideoError(""); }}
                          placeholder="https://youtube.com/watch?v=..."
                          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
                        />
                        {mediaVideoError && (
                          <p className="text-xs text-red-400 mt-1">{mediaVideoError}</p>
                        )}
                      </div>
                      <div>
                        <label className="text-xs text-slate-400 mb-1 block">
                          {language === "en" ? "Insert after section" : "Inserisci dopo sezione"}
                        </label>
                        <select
                          value={mediaVideoSection}
                          onChange={(e) => setMediaVideoSection(e.target.value)}
                          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                        >
                          <option value="hero">Hero</option>
                          <option value="about">About</option>
                          <option value="services">{language === "en" ? "Services" : "Servizi"}</option>
                          <option value="gallery">Gallery</option>
                          <option value="portfolio">Portfolio</option>
                          <option value="testimonials">Testimonials</option>
                          <option value="contact">{language === "en" ? "Contact" : "Contatti"}</option>
                        </select>
                      </div>
                      <button
                        onClick={handleAddVideo}
                        disabled={!mediaVideoUrl.trim() || addingVideo}
                        className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        {addingVideo ? (
                          <>
                            <ArrowPathIcon className="w-4 h-4 animate-spin" />
                            {language === "en" ? "Adding..." : "Aggiunta..."}
                          </>
                        ) : (
                          <>
                            <VideoCameraIcon className="w-4 h-4" />
                            {language === "en" ? "Add Video" : "Aggiungi video"}
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                </div>
              </>
            ) : showGuidePanel ? (
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

                {/* Guide Panel Content — Step-by-step */}
                <div className="flex-1 overflow-y-auto p-5 flex flex-col">
                  {/* Title */}
                  <div className="text-center mb-5">
                    <h2 className="text-lg font-bold text-white mb-1">
                      {language === "en" ? "Your site is ready!" : "Il tuo sito e' pronto!"}
                    </h2>
                    <p className="text-xs text-slate-400">
                      {language === "en"
                        ? "Follow these steps to make it perfect"
                        : "Segui questi passaggi per renderlo perfetto"}
                    </p>
                  </div>

                  {/* Step-by-step guide */}
                  <div className="space-y-2 flex-1">
                    {(language === "en" ? [
                      { step: 1, title: "Review the preview", desc: "Scroll through your site on the right. Check texts, images and layout.", icon: "1" },
                      { step: 2, title: "Refine with AI Chat", desc: "Open the Chat AI to change colors, texts, add sections or fix anything.", icon: "2", action: "Cambia i colori con toni piu' moderni e professionali" },
                      { step: 3, title: "Replace images", desc: "Click Media, upload your photos, then use 'Replace' on any site image to swap it. You can also attach photos in the Chat to insert them via AI.", icon: "3" },
                      { step: 4, title: "Add your content", desc: "Ask the AI to add testimonials, FAQ, gallery or any new section.", icon: "4", action: "Add a testimonials section with 3 reviews and a FAQ with 5 questions" },
                      { step: 5, title: "Publish", desc: "When you're satisfied, click the green Publish button to go live!", icon: "5" },
                    ] : [
                      { step: 1, title: "Controlla l'anteprima", desc: "Scorri il sito a destra. Verifica testi, immagini e layout.", icon: "1" },
                      { step: 2, title: "Modifica con Chat AI", desc: "Apri la Chat AI per cambiare colori, testi, aggiungere sezioni o correggere.", icon: "2", action: "Cambia i colori con toni piu' moderni e professionali" },
                      { step: 3, title: "Sostituisci le immagini", desc: "Clicca Media, carica le tue foto, poi usa 'Sostituisci' su un'immagine del sito per scambiarla. Puoi anche allegare foto nella Chat per inserirle tramite AI.", icon: "3" },
                      { step: 4, title: "Aggiungi contenuti", desc: "Chiedi all'AI di aggiungere testimonial, FAQ, galleria o nuove sezioni.", icon: "4", action: "Aggiungi una sezione testimonials con 3 recensioni e una FAQ con 5 domande" },
                      { step: 5, title: "Pubblica", desc: "Quando sei soddisfatto, clicca il pulsante verde Pubblica per andare online!", icon: "5" },
                    ]).map((item) => (
                      <button
                        key={item.step}
                        onClick={() => {
                          if (item.step === 2 && item.action) {
                            handleGuideSuggestionClick(item.action);
                          } else if (item.step === 3) {
                            setShowGuidePanel(false);
                            openMediaPanel();
                          } else if (item.step === 4 && item.action) {
                            handleGuideSuggestionClick(item.action);
                          } else if (item.step === 5) {
                            setShowGuidePanel(false);
                          } else {
                            // Step 1: just dismiss guide to focus on preview
                            setShowGuidePanel(false);
                          }
                        }}
                        className="w-full text-left rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 p-3.5 transition-all group"
                      >
                        <div className="flex items-start gap-3">
                          <span className="w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                            {item.icon}
                          </span>
                          <div>
                            <h4 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                              {item.title}
                            </h4>
                            <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                              {item.desc}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {/* Quick improvement suggestions */}
                  <div className="mt-4 pt-3 border-t border-white/10">
                    <p className="text-xs text-slate-500 mb-2">
                      {language === "en" ? "Quick improvements:" : "Migliorie rapide:"}
                    </p>
                    <div className="grid grid-cols-2 gap-1.5">
                      {GUIDE_SUGGESTIONS[language as "it" | "en"].map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleGuideSuggestionClick(suggestion.chatMessage)}
                          className="text-left rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 p-2.5 transition-all text-xs"
                        >
                          <span className="block text-sm mb-0.5">{suggestion.icon}</span>
                          <span className="text-white font-medium">{suggestion.title}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Bottom CTA */}
                  <div className="mt-4">
                    <button
                      onClick={handleGuideDismiss}
                      className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all"
                    >
                      {language === "en" ? "Open AI Chat" : "Apri Chat AI"}
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

              {/* Pending photos indicator */}
              {pendingPhotos.length > 0 && (
                <div className="flex items-center gap-2 px-2 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-1">
                  <PhotoIcon className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                  <span className="text-xs text-blue-300 flex-1">
                    {pendingPhotos.length} {language === "en" ? "image(s) attached" : "immagine/i allegata/e"}
                  </span>
                  <button
                    onClick={() => setPendingPhotos([])}
                    className="text-blue-400 hover:text-red-400 transition-colors"
                    title={language === "en" ? "Remove all" : "Rimuovi tutte"}
                  >
                    <XMarkIcon className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

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
                  disabled={(!chatInput.trim() && pendingPhotos.length === 0) || isRefining}
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
