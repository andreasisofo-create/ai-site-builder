"use client";

export const dynamic = "force-dynamic";
import { useState, useRef, useEffect } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import { Suspense } from "react";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckIcon,
  CloudArrowUpIcon,
  SparklesIcon,
  BuildingStorefrontIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  PhotoIcon,
  XMarkIcon,
  ChevronRightIcon,
  PlusIcon,
  TrashIcon,
  VideoCameraIcon,
  SwatchIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
} from "@heroicons/react/24/outline";
import GenerationExperience, { type PreviewData } from "@/components/GenerationExperience";
import toast from "react-hot-toast";
import { createSite, generateWebsite, generateSlug, CreateSiteData, getQuota, upgradeToPremium, getGenerationStatus, analyzeImage } from "@/lib/api";
import {
  TEMPLATE_CATEGORIES, TemplateCategory, TemplateStyle,
  SECTION_LABELS, STYLE_OPTIONS, CTA_OPTIONS, ALL_SECTIONS, STYLE_TO_MOOD,
  generateStylePreviewHtml, findStyleById,
  getSectionLabels, getStyleOptions, getCtaOptions, getAllSections,
  getCategoryLabel, getStyleLabel, getStyleDescription,
  V2_CATEGORIES, V2Category, getV2CategoryName, getV2CategoryDescription,
} from "@/lib/templates";
import { useLanguage } from "@/lib/i18n";

// ============ COLOR PALETTE UTILS ============

function hexToHsl(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0;
  const l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }
  return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

function hslToHex(h: number, s: number, l: number): string {
  s /= 100; l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, "0");
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

function generatePaletteFromPrimary(primary: string): string[] {
  const [h, s, l] = hexToHsl(primary);
  return [
    primary,
    hslToHex((h + 30) % 360, Math.min(s + 10, 100), Math.max(l - 10, 20)),
    hslToHex((h + 180) % 360, Math.max(s - 20, 20), 60),
    hslToHex(h, Math.max(s - 40, 5), 97),
    hslToHex(h, Math.max(s - 30, 10), 12),
  ];
}

// Pre-built palettes per category
const CATEGORY_PALETTES: Record<string, string[][]> = {
  ristorante: [
    ["#b8860b", "#8b4513", "#d4a843", "#faf5eb", "#1a1a0e"],
    ["#8b0000", "#5c1a1a", "#c4564a", "#fdf2f2", "#1a0a0a"],
    ["#2d5016", "#4a7c23", "#f5c542", "#f8f6f0", "#0d1a08"],
  ],
  studio_professionale: [
    ["#1a3c5e", "#0f2a40", "#3498db", "#f0f4f8", "#0a1520"],
    ["#2c3e50", "#1a252f", "#e67e22", "#f5f5f5", "#111111"],
    ["#1a365d", "#2d4a6f", "#4299e1", "#edf2f7", "#0d1b2a"],
  ],
  portfolio: [
    ["#2d3436", "#636e72", "#fdcb6e", "#f9f9f9", "#0d0d0d"],
    ["#1a1a2e", "#16213e", "#e94560", "#f5f5f5", "#0f0f1a"],
    ["#2d3436", "#00b894", "#dfe6e9", "#fafafa", "#0d0d0d"],
  ],
  fitness: [
    ["#e84393", "#a83279", "#ffeaa7", "#f9f0f5", "#1a0a14"],
    ["#ff6b35", "#cc4400", "#ffd166", "#fff8f0", "#1a0e06"],
    ["#00b894", "#008b6e", "#fdcb6e", "#f0faf6", "#0a1a14"],
  ],
  bellezza: [
    ["#c5a04b", "#a0813a", "#f5e6cc", "#faf8f4", "#1a1508"],
    ["#d4a0a0", "#b07070", "#f5d5d5", "#fdf5f5", "#1a0a0a"],
    ["#8e7cc3", "#6b5b9a", "#d9cef2", "#f8f5fd", "#140e1f"],
  ],
  salute: [
    ["#3B82F6", "#2563EB", "#93C5FD", "#f0f7ff", "#0c1a30"],
    ["#10B981", "#059669", "#6EE7B7", "#f0fdf4", "#0a1a14"],
    ["#0EA5E9", "#0284C7", "#7DD3FC", "#f0f9ff", "#0c1520"],
  ],
  saas: [
    ["#6c5ce7", "#5541d9", "#a29bfe", "#f3f0ff", "#0f0a20"],
    ["#0984e3", "#0670c4", "#74b9ff", "#f0f7ff", "#081a30"],
    ["#00cec9", "#00b5b0", "#81ecec", "#f0fdfd", "#0a1a1a"],
  ],
  ecommerce: [
    ["#10B981", "#059669", "#6EE7B7", "#f0fdf4", "#0a1a14"],
    ["#F59E0B", "#D97706", "#FCD34D", "#fffbeb", "#1a1508"],
    ["#8B5CF6", "#7C3AED", "#C4B5FD", "#f5f3ff", "#130e20"],
  ],
  artigiani: [
    ["#d35400", "#b84500", "#f39c12", "#fdf5ee", "#1a0e00"],
    ["#2980b9", "#1a5d8c", "#e67e22", "#f0f7fb", "#0c1a28"],
    ["#27ae60", "#1e8449", "#f1c40f", "#f0faf4", "#0a1a0e"],
  ],
  agenzia: [
    ["#8B5CF6", "#7C3AED", "#C4B5FD", "#f5f3ff", "#130e20"],
    ["#EC4899", "#DB2777", "#F9A8D4", "#fdf2f8", "#1a0a14"],
    ["#3B82F6", "#2563EB", "#93C5FD", "#eff6ff", "#0c1a30"],
  ],
};

// ============ V2 CATEGORY → V1 TEMPLATE STYLE MAPPING ============
// Maps V2 category slugs to V1 template_style_id pool for the databinding pipeline.
// A random style is picked each generation to ensure visual diversity.
const V2_TO_V1_STYLES: Record<string, string[]> = {
  ristorante: ["restaurant-elegant", "restaurant-cozy", "restaurant-modern"],
  studio_professionale: ["business-trust", "business-corporate", "business-fresh"],
  portfolio: ["portfolio-gallery", "portfolio-minimal", "portfolio-creative"],
  fitness: ["business-fresh", "saas-clean", "business-corporate"],
  bellezza: ["portfolio-creative", "portfolio-minimal", "ecommerce-luxury"],
  salute: ["business-corporate", "business-trust", "saas-clean"],
  saas: ["saas-gradient", "saas-clean", "saas-dark"],
  ecommerce: ["ecommerce-modern", "ecommerce-luxury"],
  artigiani: ["business-corporate", "business-fresh", "business-trust"],
  agenzia: ["saas-gradient", "saas-dark", "business-fresh"],
};

function pickRandomV1Style(v2Category: string): string {
  const pool = V2_TO_V1_STYLES[v2Category];
  if (!pool || pool.length === 0) return "business-corporate";
  return pool[Math.floor(Math.random() * pool.length)];
}

// Maps V2-specific section types to V1 equivalents (V1 has no templates for these)
const V2_SECTION_TO_V1: Record<string, string> = {
  portfolio: "gallery",
  products: "services",
  programs: "services",
  menu: "services",
  booking: "contact",
  cases: "testimonials",
};

// ============ COMPONENT ============

function NewProjectContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language } = useLanguage();
  const templateParam = searchParams.get("template");
  const styleParam = searchParams.get("style");

  // Find pre-selected category/style from dashboard
  const styleMatch = styleParam ? findStyleById(styleParam) : null;
  const initialCategory = styleMatch?.category || TEMPLATE_CATEGORIES.find(c => c.id === templateParam) || null;
  const initialStyle = styleMatch?.style || initialCategory?.styles[0] || null;

  const [currentStep, setCurrentStep] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | null>(initialCategory);
  const [selectedStyle, setSelectedStyle] = useState<TemplateStyle | null>(initialStyle);
  const [selectedV2Category, setSelectedV2Category] = useState<V2Category | null>(null);
  const [colorPalette, setColorPalette] = useState<string[]>(["#3b82f6", "#2563eb", "#93c5fd", "#f0f7ff", "#0c1a30"]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSiteId, setCreatedSiteId] = useState<number | null>(null);
  const [showAdvancedTemplate, setShowAdvancedTemplate] = useState(true);
  const [showSectionTexts, setShowSectionTexts] = useState(false);
  const logoInputRef = useRef<HTMLInputElement>(null);
  const photoInputRef = useRef<HTMLInputElement>(null);
  const refImageInput1 = useRef<HTMLInputElement>(null);
  const refImageInput2 = useRef<HTMLInputElement>(null);
  const generationRef = useRef<HTMLDivElement>(null);

  // Form state
  const [formData, setFormData] = useState({
    businessName: "",
    tagline: "",
    description: "",
    logo: null as string | null,
    photos: [] as { id: string; dataUrl: string; label: string }[],
    contactInfo: {
      address: "",
      phone: "",
      email: "",
      hours: "",
    },
    referenceImages: [null, null] as (string | null)[],
    referenceUrls: "",
    preferredStyle: "",
    heroType: "simple" as "video" | "gallery" | "simple",
    heroVideoUrl: "",
    selectedSections: ALL_SECTIONS.filter(s => s.default).map(s => s.id),
    sectionTexts: {} as Record<string, string>,
    primaryCta: "contact",
    generateImages: true,
    socialLinks: {
      facebook: "",
      instagram: "",
      linkedin: "",
      twitter: "",
    },
  });

  // Generation state
  const [generationProgress, setGenerationProgress] = useState({
    step: 0, totalSteps: 3, message: "", percentage: 0,
  });
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState(false);

  // Steps definition - 3 step wizard
  const WIZARD_STEPS = [
    { id: 0, title: language === "en" ? "Your Brand" : "Il tuo Brand", icon: BuildingStorefrontIcon },
    { id: 1, title: language === "en" ? "Content" : "Contenuti", icon: DocumentTextIcon },
    { id: 2, title: language === "en" ? "Review & Generate" : "Rivedi & Genera", icon: SparklesIcon },
  ];

  // Logo upload
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        toast.error(language === "en" ? "File too large (max 2MB)" : "File troppo grande (max 2MB)");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({ ...prev, logo: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Compress image via canvas (max 1024px, JPEG 0.8)
  const compressImageForRef = (dataUrl: string, maxWidth = 1024): Promise<string> => {
    return new Promise((resolve) => {
      const img = new window.Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        const ratio = Math.min(1, maxWidth / img.width);
        canvas.width = img.width * ratio;
        canvas.height = img.height * ratio;
        const ctx = canvas.getContext("2d");
        ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.8));
      };
      img.onerror = () => resolve(dataUrl);
      img.src = dataUrl;
    });
  };

  // Reference image upload (with compression to reduce payload)
  const handleReferenceImageUpload = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error(language === "en" ? "File too large (max 5MB)" : "File troppo grande (max 5MB)");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = async () => {
        const raw = reader.result as string;
        const compressed = await compressImageForRef(raw);
        setFormData(prev => {
          const newRefImages = [...prev.referenceImages];
          newRefImages[index] = compressed;
          return { ...prev, referenceImages: newRefImages };
        });
      };
      reader.readAsDataURL(file);
    }
  };

  // Section toggle
  const toggleSection = (sectionId: string) => {
    setFormData(prev => {
      const sections = prev.selectedSections.includes(sectionId)
        ? prev.selectedSections.filter(s => s !== sectionId)
        : [...prev.selectedSections, sectionId];
      return { ...prev, selectedSections: sections };
    });
  };

  // Photo uploads
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      if (file.size > 2 * 1024 * 1024) {
        toast.error(language === "en" ? "File too large (max 2MB)" : "File troppo grande (max 2MB)");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => {
          if (prev.photos.length >= 8) {
            toast.error(language === "en" ? "Maximum 8 photos" : "Massimo 8 foto");
            return prev;
          }
          return {
            ...prev,
            photos: [
              ...prev.photos,
              {
                id: `photo-${Date.now()}-${Math.random().toString(36).slice(2)}`,
                dataUrl: reader.result as string,
                label: file.name,
              },
            ],
          };
        });
      };
      reader.readAsDataURL(file);
    });
    // Reset input
    if (photoInputRef.current) photoInputRef.current.value = "";
  };

  const removePhoto = (photoId: string) => {
    setFormData(prev => ({
      ...prev,
      photos: prev.photos.filter(p => p.id !== photoId),
    }));
  };

  // Select category (template selection is inside Step 1, no auto-navigation)
  const selectCategory = (category: TemplateCategory) => {
    setSelectedCategory(category);
    setSelectedStyle(category.styles[0] || null);
  };

  // Select style → just update preview (user clicks "Avanti" to proceed)
  const selectStyle = (style: TemplateStyle) => {
    setSelectedStyle(style);
  };

  // Polling is handled by the /generate/[id] page after navigation

  // Generate
  const handleGenerate = async () => {
    if (isGenerating) return;
    if (!formData.businessName.trim()) {
      toast.error(language === "en" ? "Enter the business name" : "Inserisci il nome del business");
      return;
    }
    if (formData.selectedSections.length === 0) {
      toast.error(language === "en" ? "Select at least one section" : "Seleziona almeno una sezione");
      return;
    }

    setIsGenerating(true);
    setPreviewData(null);
    setGenerationProgress({ step: 0, totalSteps: 3, message: language === "en" ? "Preparing..." : "Preparazione...", percentage: 0 });

    // Scroll the generation UI into view so the user sees progress immediately
    setTimeout(() => {
      generationRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 100);

    try {
      const quota = await getQuota();
      if (!quota.has_remaining_generations) {
        setShowUpgradeModal(true);
        setIsGenerating(false);
        return;
      }

      setGenerationProgress({ step: 0, totalSteps: 3, message: language === "en" ? "Creating project..." : "Creazione progetto...", percentage: 5 });
      const siteData: CreateSiteData = {
        name: formData.businessName,
        slug: generateSlug(formData.businessName),
        description: formData.description,
      };
      const site = await createSite(siteData);
      setCreatedSiteId(site.id);

      setGenerationProgress({ step: 1, totalSteps: 3, message: language === "en" ? "Starting AI generation..." : "Avvio generazione AI...", percentage: 10 });

      // Build enriched description with all context
      const parts: string[] = [];

      if (selectedStyle && selectedCategory) {
        parts.push(`Template: ${selectedCategory.label} - Stile: ${selectedStyle.label}. ${selectedStyle.description}.`);
      } else if (formData.preferredStyle) {
        const styleLabel = STYLE_OPTIONS.find(s => s.id === formData.preferredStyle)?.label || formData.preferredStyle;
        parts.push(`Stile preferito: ${styleLabel}.`);
      }

      parts.push(`Descrizione attività: ${formData.description}`);
      if (formData.tagline) parts.push(`Slogan: ${formData.tagline}`);

      const ctaLabel = CTA_OPTIONS.find(c => c.id === formData.primaryCta)?.label || formData.primaryCta;
      parts.push(`CTA primaria: ${ctaLabel}`);

      // Section texts
      const sectionTextEntries = Object.entries(formData.sectionTexts).filter(([, v]) => v.trim());
      if (sectionTextEntries.length > 0) {
        parts.push("Testi per sezione:");
        sectionTextEntries.forEach(([key, val]) => {
          const label = SECTION_LABELS[key] || key;
          parts.push(`- ${label}: ${val}`);
        });
      }

      if (formData.referenceUrls.trim()) {
        parts.push(`Siti di riferimento: ${formData.referenceUrls}`);
      }

      const socialEntries = Object.entries(formData.socialLinks).filter(([, v]) => v.trim());
      if (socialEntries.length > 0) {
        parts.push("Social: " + socialEntries.map(([k, v]) => `${k}: ${v}`).join(", "));
      }

      const fullDescription = parts.join("\n");

      // Determine style_preferences
      let stylePrefs: { primary_color?: string; secondary_color?: string; mood?: string } | undefined;
      if (selectedStyle) {
        stylePrefs = {
          primary_color: selectedStyle.primaryColor,
          secondary_color: selectedStyle.secondaryColor,
          mood: selectedStyle.mood,
        };
      } else if (formData.preferredStyle && STYLE_TO_MOOD[formData.preferredStyle]) {
        const m = STYLE_TO_MOOD[formData.preferredStyle];
        stylePrefs = {
          primary_color: m.primaryColor,
          secondary_color: m.secondaryColor,
          mood: m.mood,
        };
      }

      // Build contact_info with hours and social
      const contactInfo: Record<string, string> = {};
      if (formData.contactInfo.address) contactInfo.address = formData.contactInfo.address;
      if (formData.contactInfo.phone) contactInfo.phone = formData.contactInfo.phone;
      if (formData.contactInfo.email) contactInfo.email = formData.contactInfo.email;
      if (formData.contactInfo.hours) contactInfo.hours = formData.contactInfo.hours;
      socialEntries.forEach(([k, v]) => { contactInfo[`social_${k}`] = v; });

      const photoUrls = formData.photos.map(p => p.dataUrl);
      const refImageUrl = formData.referenceImages.find(img => img !== null) || undefined;

      // Extract reference URLs as dedicated array
      const refUrlList = formData.referenceUrls
        .split(/[\s,]+/)
        .map(u => u.trim())
        .filter(u => u.startsWith("http://") || u.startsWith("https://"));

      // Pre-analyze reference image (non-blocking on failure)
      let refAnalysis: string | undefined;
      if (refImageUrl) {
        try {
          const result = await analyzeImage(refImageUrl);
          if (result?.analysis) refAnalysis = result.analysis;
        } catch { /* non-blocking */ }
      }

      // Always use V1 (databinding) pipeline - runs in background, saves progress, battle-tested.
      // When V2 category is selected, map it to the closest V1 template_style_id.
      const effectiveTemplateStyle = selectedStyle?.id
        || (selectedV2Category ? pickRandomV1Style(selectedV2Category.slug) : undefined);

      // If V2 category selected but no style prefs set, derive from V2 category palette
      if (selectedV2Category && !stylePrefs) {
        stylePrefs = {
          primary_color: colorPalette[0],
          secondary_color: colorPalette[1],
          mood: selectedV2Category.slug,
        };
      }

      // Map V2-specific section types to V1 equivalents
      const mappedSections = formData.selectedSections.map(
        s => V2_SECTION_TO_V1[s] || s
      );
      // Deduplicate (e.g. if both "services" and "products" → "services" map to same)
      const uniqueSections = [...new Set(mappedSections)];

      const generateResult = await generateWebsite({
        business_name: formData.businessName,
        business_description: fullDescription,
        sections: uniqueSections,
        style_preferences: stylePrefs,
        logo_url: formData.logo || undefined,
        reference_image_url: refImageUrl || (photoUrls.length > 0 ? photoUrls[0] : undefined),
        reference_analysis: refAnalysis,
        reference_urls: refUrlList.length > 0 ? refUrlList : undefined,
        photo_urls: photoUrls.length > 0 ? photoUrls : undefined,
        contact_info: Object.keys(contactInfo).length > 0 ? contactInfo : undefined,
        site_id: site.id,
        template_style_id: effectiveTemplateStyle,
        generate_images: formData.generateImages,
        hero_type: formData.heroType,
        hero_video_url: formData.heroType === "video" ? formData.heroVideoUrl : undefined,
      });

      if (!generateResult.success) throw new Error(generateResult.error || (language === "en" ? "Error starting generation" : "Errore nell'avvio della generazione"));

      // Navigate immediately to the immersive generation experience page.
      // generateWebsite() returns fast (generation runs in background on backend).
      // The /generate page handles progress polling, so no need to wait here.
      router.push(`/generate/${site.id}`);
    } catch (error: any) {
      if (error.isQuotaError || error.quota?.upgrade_required) {
        setShowUpgradeModal(true);
      } else {
        toast.error(error.message || (language === "en" ? "Generation error" : "Errore nella generazione"));
      }
      setIsGenerating(false);
      setPreviewData(null);
      setGenerationProgress({ step: 0, totalSteps: 3, message: "", percentage: 0 });
    }
  };

  const handleUpgrade = async () => {
    try {
      setIsUpgrading(true);
      await upgradeToPremium();
      toast.success(language === "en" ? "Upgrade complete!" : "Upgrade completato!");
      setShowUpgradeModal(false);
      handleGenerate();
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "Upgrade error" : "Errore nell'upgrade"));
    } finally {
      setIsUpgrading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: return !!(formData.businessName.trim() && formData.description.trim() && selectedV2Category);
      case 1: return formData.selectedSections.length > 0;
      case 2: return formData.selectedSections.length > 0;
      default: return true;
    }
  };

  // When V2 category changes, update palette and sections
  const handleV2CategorySelect = (cat: V2Category) => {
    setSelectedV2Category(cat);
    setColorPalette(generatePaletteFromPrimary(cat.defaultColor));
    // Auto-set sections from blueprint
    setFormData(prev => ({
      ...prev,
      selectedSections: cat.sectionsRequired,
    }));
  };

  const handlePrimaryColorChange = (color: string) => {
    setColorPalette(generatePaletteFromPrimary(color));
  };

  const handlePaletteSelect = (palette: string[]) => {
    setColorPalette([...palette]);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/5 z-50">
        <div className="h-full max-w-7xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => router.push("/dashboard")} className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors">
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                <SparklesIcon className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold">{language === "en" ? "New Project" : "Nuovo Progetto"}</span>
            </div>
          </div>

          {/* Step Indicator */}
          <div className="hidden md:flex items-center gap-1">
            {WIZARD_STEPS.map((step, idx) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full transition-all ${
                  currentStep === step.id ? "bg-white/10 text-white" : currentStep > step.id ? "text-emerald-400" : "text-slate-600"
                }`}>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                    currentStep === step.id ? "bg-blue-500 text-white" : currentStep > step.id ? "bg-emerald-500/20 text-emerald-400" : "bg-white/5 text-slate-600"
                  }`}>
                    {currentStep > step.id ? <CheckIcon className="w-3 h-3" /> : idx + 1}
                  </div>
                  <span className="text-xs font-medium">{step.title}</span>
                </div>
                {idx < WIZARD_STEPS.length - 1 && <ChevronRightIcon className="w-3 h-3 text-slate-700 mx-0.5" />}
              </div>
            ))}
          </div>

          <div className="w-20" />
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 pb-32 px-6">
        <div className="max-w-5xl mx-auto">

          {/* ===== STEP 0: Il tuo Brand ===== */}
          {currentStep === 0 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">{language === "en" ? "Your Brand" : "Il tuo Brand"}</h1>
                <p className="text-slate-400">{language === "en" ? "Tell us about your business — the AI will design everything else" : "Raccontaci della tua attivita' — l'AI pensera' a tutto il resto"}</p>
              </div>

              <div className="max-w-3xl mx-auto space-y-8">
                {/* Nome del sito */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Site Name" : "Nome del sito"} <span className="text-red-400">*</span></label>
                  <input
                    type="text"
                    value={formData.businessName}
                    onChange={e => setFormData(prev => ({ ...prev, businessName: e.target.value }))}
                    placeholder={language === "en" ? "e.g. Mario's Restaurant" : "es. Ristorante Da Mario"}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>

                {/* Descrizione attivita' */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Describe your business" : "Descrivi la tua attivita'"} <span className="text-red-400">*</span></label>
                  <textarea
                    value={formData.description}
                    onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder={language === "en" ? "Describe in a few words what you do, your services, your specialty..." : "Descrivi in poche parole cosa fai, i tuoi servizi, la tua specialita'..."}
                    rows={4}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                  />
                </div>

                {/* Categoria — visual card grid */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Category" : "Categoria"} <span className="text-red-400">*</span></label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                    {V2_CATEGORIES.map(cat => (
                      <button
                        key={cat.slug}
                        onClick={() => handleV2CategorySelect(cat)}
                        className={`group relative flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all text-center ${
                          selectedV2Category?.slug === cat.slug
                            ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                            : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                        }`}
                      >
                        <span className="text-2xl">{cat.icon}</span>
                        <span className={`text-sm font-medium ${selectedV2Category?.slug === cat.slug ? "text-blue-300" : "text-white"}`}>
                          {getV2CategoryName(cat, language)}
                        </span>
                        <span className="text-[10px] text-slate-500 leading-tight">
                          {getV2CategoryDescription(cat, language)}
                        </span>
                        {selectedV2Category?.slug === cat.slug && (
                          <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                            <CheckIcon className="w-3 h-3 text-white" />
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Logo Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Logo (optional)" : "Logo (opzionale)"}</label>
                  <div className="flex items-start gap-4">
                    <div
                      onClick={() => logoInputRef.current?.click()}
                      className="relative w-32 h-32 flex-shrink-0 rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer flex flex-col items-center justify-center gap-2"
                    >
                      {formData.logo ? (
                        <>
                          <Image src={formData.logo} alt="Logo" fill className="object-contain p-3" />
                          <button
                            onClick={e => { e.stopPropagation(); setFormData(prev => ({ ...prev, logo: null })); }}
                            className="absolute top-1 right-1 p-1 bg-black/60 rounded-lg hover:bg-black/80"
                          >
                            <XMarkIcon className="w-3 h-3" />
                          </button>
                        </>
                      ) : (
                        <>
                          <CloudArrowUpIcon className="w-8 h-8 text-slate-500" />
                          <p className="text-[10px] text-slate-500">PNG, JPG, SVG</p>
                        </>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 pt-2">
                      <p>{language === "en" ? "Upload your logo so the AI can extract colors and style." : "Carica il tuo logo — l'AI ne estrarra' colori e stile."}</p>
                      <p className="mt-1 text-slate-600">Max 2MB</p>
                    </div>
                  </div>
                  <input ref={logoInputRef} type="file" accept="image/*" onChange={handleLogoUpload} className="hidden" />
                </div>

                {/* Palette Colori */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Color Palette" : "Palette Colori"}</label>

                  {/* Primary color picker */}
                  <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center gap-3">
                      <label
                        className="w-12 h-12 rounded-xl border-2 border-white/20 cursor-pointer overflow-hidden transition-all hover:border-white/40"
                        style={{ backgroundColor: colorPalette[0] }}
                      >
                        <input
                          type="color"
                          value={colorPalette[0]}
                          onChange={e => handlePrimaryColorChange(e.target.value)}
                          className="opacity-0 w-full h-full cursor-pointer"
                        />
                      </label>
                      <div>
                        <p className="text-sm text-white font-medium">{language === "en" ? "Primary color" : "Colore primario"}</p>
                        <p className="text-xs text-slate-500 font-mono">{colorPalette[0]}</p>
                      </div>
                    </div>
                  </div>

                  {/* Auto-generated palette preview */}
                  <div className="flex items-center gap-2 mb-4">
                    {colorPalette.map((color, idx) => (
                      <div key={idx} className="flex flex-col items-center gap-1">
                        <div
                          className={`w-14 h-14 rounded-xl border-2 transition-all ${idx === 0 ? "border-blue-500" : "border-white/10"}`}
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-[9px] text-slate-600 font-mono">{color}</span>
                        <span className="text-[9px] text-slate-500">
                          {idx === 0 ? (language === "en" ? "Primary" : "Primario")
                            : idx === 1 ? (language === "en" ? "Secondary" : "Secondario")
                            : idx === 2 ? "Accent"
                            : idx === 3 ? (language === "en" ? "Background" : "Sfondo")
                            : (language === "en" ? "Text" : "Testo")}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Suggested palettes per category */}
                  {selectedV2Category && CATEGORY_PALETTES[selectedV2Category.slug] && (
                    <div>
                      <p className="text-xs text-slate-400 mb-2">
                        {language === "en" ? "Suggested palettes for" : "Palette suggerite per"} {getV2CategoryName(selectedV2Category, language)}:
                      </p>
                      <div className="flex gap-3">
                        {CATEGORY_PALETTES[selectedV2Category.slug].map((palette, pidx) => (
                          <button
                            key={pidx}
                            onClick={() => handlePaletteSelect(palette)}
                            className={`flex rounded-lg overflow-hidden border-2 transition-all hover:scale-105 ${
                              colorPalette[0] === palette[0] && colorPalette[1] === palette[1]
                                ? "border-blue-500 shadow-lg shadow-blue-500/20"
                                : "border-white/10 hover:border-white/30"
                            }`}
                          >
                            {palette.map((c, cidx) => (
                              <div key={cidx} className="w-8 h-10" style={{ backgroundColor: c }} />
                            ))}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 1: Contenuti ===== */}
          {currentStep === 1 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">{language === "en" ? "Content" : "Contenuti"}</h1>
                <p className="text-slate-400">{language === "en" ? "Choose your hero style, add content, and contact info" : "Scegli lo stile della hero, aggiungi contenuti e contatti"}</p>
              </div>

              <div className="max-w-3xl mx-auto space-y-8">
                {/* --- Hero Type Choice --- */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Hero Section Style" : "Stile sezione Hero"}</label>
                  <div className="grid grid-cols-3 gap-4">
                    {/* Video */}
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, heroType: "video" }))}
                      className={`group relative flex flex-col items-center gap-3 p-5 rounded-2xl border-2 transition-all ${
                        formData.heroType === "video"
                          ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                          : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                      }`}
                    >
                      <VideoCameraIcon className={`w-8 h-8 ${formData.heroType === "video" ? "text-blue-400" : "text-slate-500"}`} />
                      <span className={`text-sm font-medium ${formData.heroType === "video" ? "text-blue-300" : "text-white"}`}>
                        {language === "en" ? "Video Background" : "Video di sfondo"}
                      </span>
                      <span className="text-[10px] text-slate-500 leading-tight text-center">
                        {language === "en" ? "YouTube video as background" : "Video YouTube come sfondo"}
                      </span>
                      {formData.heroType === "video" && (
                        <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                          <CheckIcon className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>

                    {/* Gallery */}
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, heroType: "gallery" }))}
                      className={`group relative flex flex-col items-center gap-3 p-5 rounded-2xl border-2 transition-all ${
                        formData.heroType === "gallery"
                          ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                          : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                      }`}
                    >
                      <PhotoIcon className={`w-8 h-8 ${formData.heroType === "gallery" ? "text-blue-400" : "text-slate-500"}`} />
                      <span className={`text-sm font-medium ${formData.heroType === "gallery" ? "text-blue-300" : "text-white"}`}>
                        {language === "en" ? "Photo Gallery" : "Galleria foto"}
                      </span>
                      <span className="text-[10px] text-slate-500 leading-tight text-center">
                        {language === "en" ? "Photo slideshow as background" : "Slideshow di foto come sfondo"}
                      </span>
                      {formData.heroType === "gallery" && (
                        <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                          <CheckIcon className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>

                    {/* Simple */}
                    <button
                      onClick={() => setFormData(prev => ({ ...prev, heroType: "simple" }))}
                      className={`group relative flex flex-col items-center gap-3 p-5 rounded-2xl border-2 transition-all ${
                        formData.heroType === "simple"
                          ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                          : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                      }`}
                    >
                      <SwatchIcon className={`w-8 h-8 ${formData.heroType === "simple" ? "text-blue-400" : "text-slate-500"}`} />
                      <span className={`text-sm font-medium ${formData.heroType === "simple" ? "text-blue-300" : "text-white"}`}>
                        {language === "en" ? "Simple Background" : "Sfondo semplice"}
                      </span>
                      <span className="text-[10px] text-slate-500 leading-tight text-center">
                        {language === "en" ? "Gradient from your palette" : "Gradiente dalla tua palette"}
                      </span>
                      {formData.heroType === "simple" && (
                        <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                          <CheckIcon className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>
                  </div>
                </div>

                {/* --- Hero: Video URL (shown only if heroType === "video") --- */}
                {formData.heroType === "video" && (
                  <div className="p-4 rounded-xl border border-white/10 bg-white/[0.02] space-y-3">
                    <label className="block text-sm font-medium">
                      {language === "en" ? "YouTube Video URL" : "URL Video YouTube"}
                    </label>
                    <input
                      type="url"
                      value={formData.heroVideoUrl}
                      onChange={e => setFormData(prev => ({ ...prev, heroVideoUrl: e.target.value }))}
                      placeholder="https://www.youtube.com/watch?v=..."
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                    {/* YouTube thumbnail preview */}
                    {formData.heroVideoUrl && (() => {
                      const match = formData.heroVideoUrl.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
                      if (!match) return null;
                      return (
                        <div className="relative aspect-video rounded-lg overflow-hidden border border-white/10">
                          <Image src={`https://img.youtube.com/vi/${match[1]}/maxresdefault.jpg`} alt="Video thumbnail" fill className="object-cover" />
                          <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                            <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                              <div className="w-0 h-0 border-l-[18px] border-l-white border-t-[11px] border-t-transparent border-b-[11px] border-b-transparent ml-1" />
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {/* --- Hero: Gallery Photos (shown only if heroType === "gallery") --- */}
                {formData.heroType === "gallery" && (
                  <div className="p-4 rounded-xl border border-white/10 bg-white/[0.02] space-y-3">
                    <label className="block text-sm font-medium">
                      {language === "en" ? "Hero Photos (max 5)" : "Foto Hero (max 5)"}
                    </label>
                    <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
                      {formData.photos.slice(0, 5).map((photo, idx) => (
                        <div key={photo.id} className="relative aspect-square rounded-xl overflow-hidden border border-white/10 group">
                          <Image src={photo.dataUrl} alt={photo.label} fill className="object-cover" />
                          <div className="absolute top-1 left-1 px-1.5 py-0.5 bg-black/70 rounded text-[10px] text-white">{idx + 1}</div>
                          <button
                            onClick={() => removePhoto(photo.id)}
                            className="absolute top-1 right-1 p-1 bg-black/70 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/80"
                          >
                            <TrashIcon className="w-3 h-3 text-white" />
                          </button>
                        </div>
                      ))}
                      {formData.photos.length < 5 && (
                        <button
                          onClick={() => photoInputRef.current?.click()}
                          className="aspect-square rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all flex flex-col items-center justify-center gap-1"
                        >
                          <PlusIcon className="w-6 h-6 text-slate-500" />
                          <span className="text-[10px] text-slate-400">{language === "en" ? "Add" : "Aggiungi"}</span>
                        </button>
                      )}
                    </div>
                    <input ref={photoInputRef} type="file" accept="image/*" multiple onChange={handlePhotoUpload} className="hidden" />
                    <p className="text-xs text-slate-500">{language === "en" ? "These photos will be used as a slideshow in the hero section" : "Queste foto verranno usate come slideshow nella sezione hero"}</p>
                  </div>
                )}

                {/* --- Hero: Simple preview (shown only if heroType === "simple") --- */}
                {formData.heroType === "simple" && colorPalette.length >= 2 && (
                  <div className="p-4 rounded-xl border border-white/10 bg-white/[0.02] space-y-2">
                    <label className="block text-sm font-medium mb-1">{language === "en" ? "Preview" : "Anteprima"}</label>
                    <div
                      className="h-32 rounded-xl flex items-center justify-center"
                      style={{ background: `linear-gradient(135deg, ${colorPalette[0]}, ${colorPalette[1]})` }}
                    >
                      <span className="text-white/80 text-sm font-medium">{formData.tagline || formData.businessName || (language === "en" ? "Your headline here" : "Il tuo slogan qui")}</span>
                    </div>
                  </div>
                )}

                {/* --- Slogan & Subtitle --- */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-2">Slogan / Headline</label>
                    <input
                      type="text"
                      value={formData.tagline}
                      onChange={e => setFormData(prev => ({ ...prev, tagline: e.target.value }))}
                      placeholder={language === "en" ? "e.g. The authentic taste of tradition" : "es. Il gusto autentico della tradizione"}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                    <p className="text-xs text-slate-500 mt-1">{language === "en" ? "Leave blank for AI-generated text" : "Lascia vuoto per generazione automatica AI"}</p>
                  </div>
                </div>

                {/* --- Per-Section Content (from category blueprint) --- */}
                {selectedV2Category && (
                  <div className="border border-white/10 rounded-2xl overflow-hidden">
                    <button
                      onClick={() => setShowSectionTexts(!showSectionTexts)}
                      className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <DocumentTextIcon className="w-5 h-5 text-emerald-400" />
                        <span className="font-medium">{language === "en" ? "Custom text per section" : "Testi personalizzati per sezione"}</span>
                        <span className="text-xs text-slate-500">({language === "en" ? "optional" : "opzionale"})</span>
                      </div>
                      <ChevronRightIcon className={`w-4 h-4 text-slate-400 transition-transform ${showSectionTexts ? "rotate-90" : ""}`} />
                    </button>

                    {showSectionTexts && (
                      <div className="px-6 pb-6 space-y-4 border-t border-white/5 pt-4">
                        {selectedV2Category.sectionsRequired
                          .filter(s => s !== "hero" && s !== "footer")
                          .map(sectionId => {
                            const sectionLabel = getSectionLabels(language)[sectionId] || sectionId;
                            return (
                              <div key={sectionId}>
                                <label className="text-sm text-slate-300 mb-1.5 block">{sectionLabel}</label>
                                <textarea
                                  value={formData.sectionTexts[sectionId] || ""}
                                  onChange={e => setFormData(prev => ({
                                    ...prev,
                                    sectionTexts: { ...prev.sectionTexts, [sectionId]: e.target.value }
                                  }))}
                                  placeholder={language === "en" ? "Leave blank for automatic AI generation" : "Lascia vuoto per generazione automatica AI"}
                                  rows={2}
                                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                                />
                              </div>
                            );
                          })}
                      </div>
                    )}
                  </div>
                )}

                {/* --- Gallery Photos (for gallery section, separate from hero) --- */}
                {selectedV2Category?.sectionsRequired.includes("gallery") && (
                  <div>
                    <label className="block text-sm font-medium mb-3">
                      {language === "en" ? "Gallery Photos (optional, max 8)" : "Foto Galleria (opzionale, max 8)"}
                    </label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      {formData.photos.map((photo, idx) => (
                        <div key={photo.id} className="relative aspect-square rounded-xl overflow-hidden border border-white/10 group">
                          <Image src={photo.dataUrl} alt={photo.label} fill className="object-cover" />
                          <div className="absolute top-1 left-1 px-1.5 py-0.5 bg-black/70 rounded text-[10px] text-white">{idx + 1}</div>
                          <button
                            onClick={() => removePhoto(photo.id)}
                            className="absolute top-1 right-1 p-1 bg-black/70 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/80"
                          >
                            <TrashIcon className="w-3 h-3 text-white" />
                          </button>
                        </div>
                      ))}
                      {formData.photos.length < 8 && (
                        <button
                          onClick={() => photoInputRef.current?.click()}
                          className="aspect-square rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all flex flex-col items-center justify-center gap-1"
                        >
                          <PlusIcon className="w-6 h-6 text-slate-500" />
                          <span className="text-[10px] text-slate-400">{language === "en" ? "Add" : "Aggiungi"}</span>
                        </button>
                      )}
                    </div>
                    <input ref={photoInputRef} type="file" accept="image/*" multiple onChange={handlePhotoUpload} className="hidden" />
                    <p className="text-xs text-slate-500 mt-2">
                      {language === "en" ? "Without photos, AI will use professional stock images." : "Senza foto, l'AI usera' immagini professionali di stock."}
                    </p>
                  </div>
                )}

                {/* --- Contact Info --- */}
                <div className="pt-4 border-t border-white/10">
                  <label className="block text-sm font-medium mb-4 flex items-center gap-2">
                    <MapPinIcon className="w-4 h-4 text-slate-400" />
                    {language === "en" ? "Contact information" : "Informazioni di contatto"}
                  </label>
                  <div className="space-y-3">
                    <input
                      type="text"
                      value={formData.contactInfo.address}
                      onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, address: e.target.value } }))}
                      placeholder={language === "en" ? "Address: 123 Main Street, New York" : "Indirizzo: Via Roma 123, 00100 Roma"}
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                    <div className="grid sm:grid-cols-2 gap-3">
                      <div className="relative">
                        <PhoneIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                          type="tel"
                          value={formData.contactInfo.phone}
                          onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, phone: e.target.value } }))}
                          placeholder={language === "en" ? "Phone" : "Telefono"}
                          className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                        />
                      </div>
                      <div className="relative">
                        <EnvelopeIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                          type="email"
                          value={formData.contactInfo.email}
                          onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, email: e.target.value } }))}
                          placeholder="Email"
                          className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                        />
                      </div>
                    </div>
                    <input
                      type="text"
                      value={formData.contactInfo.hours}
                      onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, hours: e.target.value } }))}
                      placeholder={language === "en" ? "Opening hours: e.g. Mon-Fri 9:00-18:00" : "Orari: es. Lun-Ven 9:00-18:00, Sab 9:00-13:00"}
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                  </div>
                </div>

                {/* --- Social Links --- */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Social Links (optional)" : "Social Links (opzionale)"}</label>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {(["instagram", "facebook", "linkedin", "twitter"] as const).map(social => (
                      <div key={social} className="flex items-center gap-2">
                        <span className="text-xs text-slate-400 w-20 capitalize">{social === "twitter" ? "X / Twitter" : social}</span>
                        <input
                          type="text"
                          value={formData.socialLinks[social]}
                          onChange={e => setFormData(prev => ({
                            ...prev,
                            socialLinks: { ...prev.socialLinks, [social]: e.target.value }
                          }))}
                          placeholder={`URL ${social}`}
                          className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 2: Rivedi & Genera ===== */}
          {currentStep === 2 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold mb-3">{language === "en" ? "Review & Generate" : "Rivedi & Genera"}</h1>
                <p className="text-slate-400">{language === "en" ? "Check everything looks good, then generate your site" : "Controlla che tutto sia corretto, poi genera il tuo sito"}</p>
              </div>

              <div className="max-w-3xl mx-auto space-y-6">

                {/* --- Summary Cards --- */}
                <div className="grid sm:grid-cols-2 gap-3 text-sm">
                  <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <span className="text-slate-500">Business:</span>{" "}
                    <span className="text-white">{formData.businessName || "\u2014"}</span>
                  </div>
                  {selectedV2Category && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                      <span className="text-slate-500">{language === "en" ? "Category:" : "Categoria:"}</span>
                      <span className="text-lg">{selectedV2Category.icon}</span>
                      <span className="text-white">{getV2CategoryName(selectedV2Category, language)}</span>
                    </div>
                  )}
                  {colorPalette.length > 0 && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                      <span className="text-slate-500">{language === "en" ? "Palette:" : "Palette:"}</span>
                      <div className="flex gap-1">
                        {colorPalette.map((c, i) => (
                          <div key={i} className="w-5 h-5 rounded" style={{ backgroundColor: c }} />
                        ))}
                      </div>
                    </div>
                  )}
                  {formData.tagline && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">{language === "en" ? "Tagline:" : "Slogan:"}</span>{" "}
                      <span className="text-white">{formData.tagline}</span>
                    </div>
                  )}
                  <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <span className="text-slate-500">{language === "en" ? "Hero:" : "Hero:"}</span>{" "}
                    <span className="text-white">
                      {formData.heroType === "video" ? (language === "en" ? "Video Background" : "Video di sfondo")
                        : formData.heroType === "gallery" ? (language === "en" ? "Photo Gallery" : "Galleria foto")
                        : (language === "en" ? "Simple Background" : "Sfondo semplice")}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <span className="text-slate-500">{language === "en" ? "Sections:" : "Sezioni:"}</span>{" "}
                    <span className="text-white">{formData.selectedSections.length}</span>
                  </div>
                  {formData.photos.length > 0 && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">{language === "en" ? "Photos:" : "Foto:"}</span>{" "}
                      <span className="text-white">{formData.photos.length}</span>
                    </div>
                  )}
                  {formData.logo && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                      <span className="text-slate-500">Logo:</span>
                      <div className="w-6 h-6 rounded overflow-hidden relative"><Image src={formData.logo} alt="Logo" fill className="object-contain" /></div>
                    </div>
                  )}
                  {(formData.contactInfo.phone || formData.contactInfo.email) && (
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">{language === "en" ? "Contact:" : "Contatti:"}</span>{" "}
                      <span className="text-white">{[formData.contactInfo.phone, formData.contactInfo.email].filter(Boolean).join(", ")}</span>
                    </div>
                  )}
                </div>

                {/* --- Sections List --- */}
                {selectedV2Category && (
                  <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                    <p className="text-xs text-slate-400 mb-2">{language === "en" ? "Sections included:" : "Sezioni incluse:"}</p>
                    <div className="flex flex-wrap gap-2">
                      {formData.selectedSections.map(sectionId => (
                        <span key={sectionId} className="px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-300 text-xs border border-blue-500/20">
                          {getSectionLabels(language)[sectionId] || sectionId}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* --- AI Image Generation Toggle --- */}
                <div>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, generateImages: !prev.generateImages }))}
                    className="w-full flex items-center justify-between px-5 py-4 rounded-2xl border border-white/10 hover:border-white/20 bg-white/[0.02] transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                        formData.generateImages ? "bg-violet-500/20" : "bg-white/5"
                      }`}>
                        <PhotoIcon className={`w-5 h-5 ${formData.generateImages ? "text-violet-400" : "text-slate-500"}`} />
                      </div>
                      <div className="text-left">
                        <span className="block text-sm font-medium text-white">
                          {language === "en" ? "Generate AI images" : "Genera immagini AI"}
                        </span>
                        <span className="block text-xs text-slate-500">
                          {language === "en"
                            ? "Create professional images that match your brand"
                            : "Crea immagini professionali che si abbinano al tuo brand"}
                        </span>
                      </div>
                    </div>
                    <div className={`w-11 h-6 rounded-full transition-colors relative ${
                      formData.generateImages ? "bg-violet-500" : "bg-white/10"
                    }`}>
                      <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform ${
                        formData.generateImages ? "translate-x-[22px]" : "translate-x-0.5"
                      }`} />
                    </div>
                  </button>
                </div>

                {/* --- Generate Button --- */}
                <div className="pt-4 space-y-4">
                  {isGenerating ? (
                    <div ref={generationRef} className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                      <GenerationExperience
                        step={generationProgress.step}
                        totalSteps={generationProgress.totalSteps}
                        message={generationProgress.message}
                        percentage={generationProgress.percentage}
                        previewData={previewData}
                      />
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={handleGenerate}
                        disabled={!canProceed()}
                        className="w-full py-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl font-semibold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <SparklesIcon className="w-5 h-5" />
                        {language === "en" ? "Generate My Site" : "Genera il Mio Sito"}
                      </button>
                      <p className="text-center text-sm text-slate-500">
                        {language === "en" ? "AI pipeline — Estimated time: 40-60 seconds" : "Pipeline AI — Tempo stimato: 40-60 secondi"}
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer Navigation */}
      <footer className="fixed bottom-0 left-0 right-0 h-20 bg-[#0a0a0a]/95 backdrop-blur-xl border-t border-white/5">
        <div className="h-full max-w-7xl mx-auto px-6 flex items-center justify-between">
          <button
            onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
            disabled={currentStep === 0 || isGenerating}
            className="flex items-center gap-2 px-6 py-2.5 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            {language === "en" ? "Back" : "Indietro"}
          </button>

          <div className="md:hidden text-sm text-slate-400">
            {language === "en" ? `Step ${currentStep + 1} of ${WIZARD_STEPS.length}` : `Passo ${currentStep + 1} di ${WIZARD_STEPS.length}`}
          </div>

          <button
            onClick={() => {
              if (currentStep === 2) {
                handleGenerate();
              } else {
                setCurrentStep(prev => Math.min(2, prev + 1));
              }
            }}
            disabled={!canProceed() || isGenerating}
            className="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-full font-medium transition-all"
          >
            {currentStep === 2 ? (language === "en" ? "Generate" : "Genera") : (language === "en" ? "Next" : "Avanti")}
            <ArrowRightIcon className="w-4 h-4" />
          </button>
        </div>
      </footer>

      {/* Upgrade Modal */}
      <Transition appear show={showUpgradeModal} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setShowUpgradeModal(false)}>
          <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0">
            <div className="fixed inset-0 bg-black/80" />
          </Transition.Child>
          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-200" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-[#111] border border-white/10 p-6 text-left align-middle shadow-xl transition-all">
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
                      <SparklesIcon className="w-8 h-8 text-white" />
                    </div>
                    <Dialog.Title as="h3" className="text-xl font-semibold mb-2">
                      {language === "en" ? "Free generations exhausted" : "Hai esaurito le generazioni gratuite"}
                    </Dialog.Title>
                    <p className="text-slate-400 mb-6">
                      {language === "en" ? "Upgrade to a paid plan for more generations." : "Passa a un piano a pagamento per piu' generazioni."}
                    </p>
                    <div className="flex gap-3">
                      <button onClick={() => setShowUpgradeModal(false)} className="flex-1 px-4 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                        {language === "en" ? "Later" : "Piu' tardi"}
                      </button>
                      <button onClick={handleUpgrade} disabled={isUpgrading} className="flex-1 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 rounded-lg font-medium transition-all disabled:opacity-50">
                        {isUpgrading ? (language === "en" ? "Activating..." : "Attivazione...") : (language === "en" ? "Upgrade (DEMO)" : "Upgrade (DEMO)")}
                      </button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}

export default function NewProjectPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <NewProjectContent />
    </Suspense>
  );
}
