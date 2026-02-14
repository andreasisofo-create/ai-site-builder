"use client";

export const dynamic = "force-dynamic";
import { useState, useRef } from "react";
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
} from "@heroicons/react/24/outline";
import GenerationExperience, { type PreviewData } from "@/components/GenerationExperience";
import toast from "react-hot-toast";
import { createSite, generateWebsite, updateSite, generateSlug, CreateSiteData, getQuota, upgradeToPremium, getGenerationStatus } from "@/lib/api";
import {
  TEMPLATE_CATEGORIES, TemplateCategory, TemplateStyle,
  SECTION_LABELS, STYLE_OPTIONS, CTA_OPTIONS, ALL_SECTIONS, STYLE_TO_MOOD,
  generateStylePreviewHtml, findStyleById,
} from "@/lib/templates";
import { useLanguage } from "@/lib/i18n";

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
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSiteId, setCreatedSiteId] = useState<number | null>(null);
  const [showAdvancedTemplate, setShowAdvancedTemplate] = useState(true);
  const [showSectionTexts, setShowSectionTexts] = useState(false);
  const logoInputRef = useRef<HTMLInputElement>(null);
  const photoInputRef = useRef<HTMLInputElement>(null);
  const refImageInput1 = useRef<HTMLInputElement>(null);
  const refImageInput2 = useRef<HTMLInputElement>(null);

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
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState(false);

  // Steps definition - 3 step wizard
  const WIZARD_STEPS = [
    { id: 0, title: "Brand & Info", icon: BuildingStorefrontIcon },
    { id: 1, title: language === "en" ? "Inspiration" : "Ispirazione", icon: PaintBrushIcon },
    { id: 2, title: language === "en" ? "Content" : "Contenuti", icon: DocumentTextIcon },
  ];

  // Logo upload
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({ ...prev, logo: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Reference image upload
  const handleReferenceImageUpload = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => {
          const newRefImages = [...prev.referenceImages];
          newRefImages[index] = reader.result as string;
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
      if (formData.photos.length >= 8) {
        toast.error(language === "en" ? "Maximum 8 photos" : "Massimo 8 foto");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          photos: [
            ...prev.photos,
            {
              id: `photo-${Date.now()}-${Math.random().toString(36).slice(2)}`,
              dataUrl: reader.result as string,
              label: file.name,
            },
          ],
        }));
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

  // Progress polling
  const startProgressPolling = (siteId: number) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const genStatus = await getGenerationStatus(siteId);
        setGenerationProgress({
          step: genStatus.step,
          totalSteps: genStatus.total_steps,
          message: genStatus.message,
          percentage: genStatus.percentage,
        });
        if (genStatus.preview_data) setPreviewData(genStatus.preview_data);

        if (!genStatus.is_generating && genStatus.status === "ready") {
          stopProgressPolling();
          setGenerationProgress({ step: 3, totalSteps: 3, message: language === "en" ? "Complete!" : "Completato!", percentage: 100 });
          toast.success(language === "en" ? "Site generated successfully!" : "Sito generato con successo!");
          setTimeout(() => router.push(`/editor/${siteId}`), 1000);
        }
        if (!genStatus.is_generating && genStatus.status === "draft" && genStatus.message) {
          stopProgressPolling();
          setIsGenerating(false);
          toast.error(genStatus.message || (language === "en" ? "Generation error" : "Errore nella generazione"));
        }
      } catch { /* ignore */ }
    }, 3000);
  };

  const stopProgressPolling = () => {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => { stopProgressPolling(); };
  }, []);

  // Generate
  const handleGenerate = async () => {
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
      startProgressPolling(site.id);

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

      const generateResult = await generateWebsite({
        business_name: formData.businessName,
        business_description: fullDescription,
        sections: formData.selectedSections,
        style_preferences: stylePrefs,
        logo_url: formData.logo || undefined,
        reference_image_url: refImageUrl || (photoUrls.length > 0 ? photoUrls[0] : undefined),
        photo_urls: photoUrls.length > 0 ? photoUrls : undefined,
        contact_info: Object.keys(contactInfo).length > 0 ? contactInfo : undefined,
        site_id: site.id,
        template_style_id: selectedStyle?.id,
        generate_images: formData.generateImages,
      });

      if (!generateResult.success) throw new Error(generateResult.error || (language === "en" ? "Error starting generation" : "Errore nell'avvio della generazione"));

      await updateSite(site.id, {
        thumbnail: `https://placehold.co/600x400/1a1a1a/666?text=${encodeURIComponent(formData.businessName)}`,
      });

      toast.success(language === "en" ? "Generation started! Please wait..." : "Generazione avviata! Attendere...");
    } catch (error: any) {
      stopProgressPolling();
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
      case 0: return !!(formData.businessName.trim() && formData.description.trim());
      case 1: return true; // Everything optional
      case 2: return formData.selectedSections.length > 0;
      default: return true;
    }
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

          {/* ===== STEP 0: Brand & Info ===== */}
          {currentStep === 0 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Brand & Info</h1>
                <p className="text-slate-400">{language === "en" ? "Tell us about your business to personalize the site" : "Raccontaci del tuo business per personalizzare il sito"}</p>
              </div>

              <div className="max-w-2xl mx-auto space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Business Name" : "Nome del Business"} <span className="text-red-400">*</span></label>
                  <input
                    type="text"
                    value={formData.businessName}
                    onChange={e => setFormData(prev => ({ ...prev, businessName: e.target.value }))}
                    placeholder={language === "en" ? "e.g. Mario's Restaurant" : "es. Ristorante Da Mario"}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Business description" : "Descrizione dell'attivita'"} <span className="text-red-400">*</span></label>
                  <textarea
                    value={formData.description}
                    onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder={language === "en" ? "Describe what you do, your services, your story... The more details you provide, the better the result." : "Descrivi cosa fai, i tuoi servizi, la tua storia... Piu' dettagli fornisci, migliore sara' il risultato."}
                    rows={5}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                  />
                </div>

                {/* Logo Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Logo (optional)" : "Logo (opzionale)"}</label>
                  <div
                    onClick={() => logoInputRef.current?.click()}
                    className="relative aspect-video max-w-xs rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer flex flex-col items-center justify-center gap-3"
                  >
                    {formData.logo ? (
                      <>
                        <Image src={formData.logo} alt="Logo" fill className="object-contain p-4" />
                        <button
                          onClick={e => { e.stopPropagation(); setFormData(prev => ({ ...prev, logo: null })); }}
                          className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-lg hover:bg-black/80"
                        >
                          <XMarkIcon className="w-4 h-4" />
                        </button>
                      </>
                    ) : (
                      <>
                        <CloudArrowUpIcon className="w-10 h-10 text-slate-500" />
                        <p className="text-sm text-slate-400">{language === "en" ? "Click to upload logo" : "Clicca per caricare il logo"}</p>
                        <p className="text-xs text-slate-600">PNG, JPG, SVG (max 2MB)</p>
                      </>
                    )}
                  </div>
                  <input ref={logoInputRef} type="file" accept="image/*" onChange={handleLogoUpload} className="hidden" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Slogan / Tagline (optional)" : "Slogan / Tagline (opzionale)"}</label>
                  <input
                    type="text"
                    value={formData.tagline}
                    onChange={e => setFormData(prev => ({ ...prev, tagline: e.target.value }))}
                    placeholder="es. Il vero gusto della tradizione"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 1: Ispirazione ===== */}
          {currentStep === 1 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">{language === "en" ? "Inspiration" : "Ispirazione"}</h1>
                <p className="text-slate-400">{language === "en" ? "Help us understand the look you want (all optional)" : "Aiutaci a capire il look che desideri (tutto opzionale)"}</p>
              </div>

              <div className="max-w-3xl mx-auto space-y-8">
                {/* Reference Images */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Reference screenshots (optional)" : "Screenshot di riferimento (opzionale)"}</label>
                  <div className="grid grid-cols-2 gap-4">
                    {[0, 1].map(idx => (
                      <div
                        key={idx}
                        onClick={() => (idx === 0 ? refImageInput1 : refImageInput2).current?.click()}
                        className="relative aspect-video rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer flex flex-col items-center justify-center gap-2"
                      >
                        {formData.referenceImages[idx] ? (
                          <>
                            <Image src={formData.referenceImages[idx]!} alt={`Riferimento ${idx + 1}`} fill className="object-cover rounded-xl" />
                            <button
                              onClick={e => {
                                e.stopPropagation();
                                setFormData(prev => {
                                  const newRefs = [...prev.referenceImages];
                                  newRefs[idx] = null;
                                  return { ...prev, referenceImages: newRefs };
                                });
                              }}
                              className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-lg hover:bg-black/80 z-10"
                            >
                              <XMarkIcon className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <>
                            <CloudArrowUpIcon className="w-8 h-8 text-slate-500" />
                            <p className="text-xs text-slate-400">Screenshot #{idx + 1}</p>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                  <input ref={refImageInput1} type="file" accept="image/*" onChange={handleReferenceImageUpload(0)} className="hidden" />
                  <input ref={refImageInput2} type="file" accept="image/*" onChange={handleReferenceImageUpload(1)} className="hidden" />
                  <p className="text-xs text-slate-500 mt-2">{language === "en" ? "Upload screenshots of websites you like as visual reference" : "Carica screenshot di siti che ti piacciono come riferimento visivo"}</p>
                </div>

                {/* Reference URLs */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Favorite site URLs (optional)" : "URL siti preferiti (opzionale)"}</label>
                  <input
                    type="text"
                    value={formData.referenceUrls}
                    onChange={e => setFormData(prev => ({ ...prev, referenceUrls: e.target.value }))}
                    placeholder="es. www.esempio1.it, www.esempio2.it"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>

                {/* Preferred Style */}
                <div>
                  <label className="block text-sm font-medium mb-2">{language === "en" ? "Preferred style" : "Stile preferito"}</label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {STYLE_OPTIONS.map(style => (
                      <button
                        key={style.id}
                        onClick={() => setFormData(prev => ({ ...prev, preferredStyle: prev.preferredStyle === style.id ? "" : style.id }))}
                        className={`px-4 py-3 rounded-xl border-2 text-sm font-medium transition-all ${
                          formData.preferredStyle === style.id
                            ? "border-blue-500 bg-blue-500/10 text-blue-400"
                            : "border-white/10 text-slate-300 hover:border-white/30"
                        }`}
                      >
                        {style.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Collapsible Advanced Template */}
                <div className="border border-white/10 rounded-2xl overflow-hidden">
                  <button
                    onClick={() => setShowAdvancedTemplate(!showAdvancedTemplate)}
                    className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <PaintBrushIcon className="w-5 h-5 text-violet-400" />
                      <span className="font-medium">{language === "en" ? "Advanced template" : "Template avanzato"}</span>
                      <span className="text-xs text-slate-500">({language === "en" ? "optional" : "opzionale"})</span>
                    </div>
                    <ChevronRightIcon className={`w-4 h-4 text-slate-400 transition-transform ${showAdvancedTemplate ? "rotate-90" : ""}`} />
                  </button>

                  {showAdvancedTemplate && (
                    <div className="px-6 pb-6 space-y-6 border-t border-white/5">
                      {/* Category selector */}
                      <div className="pt-4">
                        <label className="block text-xs text-slate-400 mb-3">{language === "en" ? "Choose category" : "Scegli categoria"}</label>
                        <div className="flex flex-wrap gap-2">
                          {TEMPLATE_CATEGORIES.map(category => (
                            <button
                              key={category.id}
                              onClick={() => selectCategory(category)}
                              className={`px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-all ${
                                selectedCategory?.id === category.id
                                  ? "bg-blue-500/20 border border-blue-500/50 text-blue-300"
                                  : "bg-white/5 border border-white/10 text-slate-400 hover:text-white"
                              }`}
                            >
                              <span>{category.icon}</span>
                              <span>{category.label}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Style cards + Preview */}
                      {selectedCategory && (
                        <div className="space-y-4">
                          <label className="block text-xs text-slate-400">{language === "en" ? `Choose style for ${selectedCategory.label}` : `Scegli stile per ${selectedCategory.label}`}</label>
                          <div className="flex gap-4 h-[50vh]">
                            {/* Style sidebar */}
                            <div className="w-56 flex-shrink-0 space-y-2 overflow-y-auto pr-2">
                              {selectedCategory.styles.map(style => (
                                <button
                                  key={style.id}
                                  onClick={() => selectStyle(style)}
                                  className={`w-full group relative rounded-xl overflow-hidden border-2 transition-all text-left ${
                                    selectedStyle?.id === style.id
                                      ? "border-blue-500 shadow-lg shadow-blue-500/20"
                                      : "border-white/10 hover:border-white/30"
                                  }`}
                                >
                                  <div className="aspect-[16/9] relative">
                                    <Image src={style.image} alt={style.label} fill className="object-cover" />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                                  </div>
                                  <div className="p-2 bg-[#111]">
                                    <div className="flex items-center gap-1.5 mb-0.5">
                                      <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: style.primaryColor }} />
                                      <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: style.secondaryColor }} />
                                      <span className="text-xs font-medium text-white ml-auto">{style.label}</span>
                                    </div>
                                    <p className="text-[10px] text-slate-400">{style.description}</p>
                                  </div>
                                  {selectedStyle?.id === style.id && (
                                    <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                                      <CheckIcon className="w-3 h-3 text-white" />
                                    </div>
                                  )}
                                </button>
                              ))}
                            </div>

                            {/* Preview */}
                            <div className="flex-1 rounded-xl border border-white/10 overflow-hidden bg-[#111] flex flex-col">
                              {selectedStyle ? (
                                <>
                                  <div className="flex items-center gap-3 px-3 py-2 border-b border-white/10 bg-[#0a0a0a]">
                                    <div className="flex gap-1.5">
                                      <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                                      <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                                    </div>
                                    <div className="flex-1 text-center">
                                      <span className="text-[11px] text-slate-400">{selectedStyle.label}</span>
                                    </div>
                                  </div>
                                  <div className="flex-1 overflow-hidden">
                                    <iframe
                                      srcDoc={generateStylePreviewHtml(selectedStyle, selectedCategory.label)}
                                      className="w-full h-full border-0"
                                      title={`Preview ${selectedStyle.label}`}
                                      sandbox="allow-same-origin"
                                    />
                                  </div>
                                </>
                              ) : (
                                <div className="flex-1 flex items-center justify-center text-slate-500">
                                  <p className="text-sm">{language === "en" ? "Select a style for preview" : "Seleziona uno stile per l'anteprima"}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 2: Contenuti & Genera ===== */}
          {currentStep === 2 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold mb-3">{language === "en" ? "Content & Generate" : "Contenuti & Genera"}</h1>
                <p className="text-slate-400">{language === "en" ? "Customize sections, contacts, and generate your site" : "Personalizza le sezioni, i contatti e genera il tuo sito"}</p>
              </div>

              <div className="max-w-3xl mx-auto space-y-8">

                {/* --- Sections Checkbox Grid --- */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Site sections" : "Sezioni del sito"} <span className="text-red-400">*</span></label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {ALL_SECTIONS.map(section => (
                      <button
                        key={section.id}
                        onClick={() => toggleSection(section.id)}
                        className={`px-3 py-2.5 rounded-xl border-2 text-sm text-left transition-all flex items-center gap-2 ${
                          formData.selectedSections.includes(section.id)
                            ? "border-blue-500 bg-blue-500/10 text-blue-300"
                            : "border-white/10 text-slate-400 hover:border-white/30"
                        }`}
                      >
                        <div className={`w-4 h-4 rounded flex-shrink-0 flex items-center justify-center border ${
                          formData.selectedSections.includes(section.id)
                            ? "bg-blue-500 border-blue-500"
                            : "border-white/20"
                        }`}>
                          {formData.selectedSections.includes(section.id) && <CheckIcon className="w-3 h-3 text-white" />}
                        </div>
                        <span className="truncate">{section.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* --- Section Texts (collapsible) --- */}
                {formData.selectedSections.length > 0 && (
                  <div className="border border-white/10 rounded-2xl overflow-hidden">
                    <button
                      onClick={() => setShowSectionTexts(!showSectionTexts)}
                      className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/[0.02] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <DocumentTextIcon className="w-5 h-5 text-emerald-400" />
                        <span className="font-medium">{language === "en" ? "Section texts" : "Testi per sezione"}</span>
                        <span className="text-xs text-slate-500">({language === "en" ? "optional" : "opzionale"})</span>
                      </div>
                      <ChevronRightIcon className={`w-4 h-4 text-slate-400 transition-transform ${showSectionTexts ? "rotate-90" : ""}`} />
                    </button>

                    {showSectionTexts && (
                      <div className="px-6 pb-6 space-y-4 border-t border-white/5 pt-4">
                        {formData.selectedSections.map(sectionId => (
                          <div key={sectionId}>
                            <div className="flex items-center justify-between mb-1.5">
                              <label className="text-sm text-slate-300">{SECTION_LABELS[sectionId] || sectionId}</label>
                              <button
                                className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1 opacity-50 cursor-not-allowed"
                                title="Disponibile prossimamente"
                                disabled
                              >
                                <SparklesIcon className="w-3 h-3" />
                                Genera testo AI
                              </button>
                            </div>
                            <textarea
                              value={formData.sectionTexts[sectionId] || ""}
                              onChange={e => setFormData(prev => ({
                                ...prev,
                                sectionTexts: { ...prev.sectionTexts, [sectionId]: e.target.value }
                              }))}
                              placeholder={`Testo per la sezione ${SECTION_LABELS[sectionId] || sectionId}...`}
                              rows={2}
                              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* --- Contact Info --- */}
                <div className="pt-4 border-t border-white/10">
                  <label className="block text-sm font-medium mb-4">{language === "en" ? "Contact information" : "Informazioni di contatto"}</label>
                  <div className="space-y-3">
                    <input
                      type="text"
                      value={formData.contactInfo.address}
                      onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, address: e.target.value } }))}
                      placeholder="Indirizzo: Via Roma 123, 00100 Roma"
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                    <div className="grid sm:grid-cols-2 gap-3">
                      <input
                        type="tel"
                        value={formData.contactInfo.phone}
                        onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, phone: e.target.value } }))}
                        placeholder="Telefono"
                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                      />
                      <input
                        type="email"
                        value={formData.contactInfo.email}
                        onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, email: e.target.value } }))}
                        placeholder="Email"
                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                      />
                    </div>
                    <input
                      type="text"
                      value={formData.contactInfo.hours}
                      onChange={e => setFormData(prev => ({ ...prev, contactInfo: { ...prev.contactInfo, hours: e.target.value } }))}
                      placeholder="Orari apertura: es. Lun-Ven 9:00-18:00, Sab 9:00-13:00"
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                    />
                  </div>
                </div>

                {/* --- Social Links --- */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Social Links (optional)" : "Social Links (opzionale)"}</label>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {(["facebook", "instagram", "linkedin", "twitter"] as const).map(social => (
                      <div key={social} className="flex items-center gap-2">
                        <span className="text-xs text-slate-400 w-20 capitalize">{social}</span>
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

                {/* --- CTA Primaria --- */}
                <div>
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Primary Call-to-Action" : "Call-to-Action primaria"}</label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {CTA_OPTIONS.map(cta => (
                      <button
                        key={cta.id}
                        onClick={() => setFormData(prev => ({ ...prev, primaryCta: cta.id }))}
                        className={`px-4 py-2.5 rounded-xl border-2 text-sm font-medium transition-all ${
                          formData.primaryCta === cta.id
                            ? "border-blue-500 bg-blue-500/10 text-blue-300"
                            : "border-white/10 text-slate-400 hover:border-white/30"
                        }`}
                      >
                        {cta.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* --- Photos --- */}
                <div className="pt-4 border-t border-white/10">
                  <label className="block text-sm font-medium mb-3">{language === "en" ? "Photos of your business (optional, max 8)" : "Foto della tua attivit\u00E0 (opzionale, max 8)"}</label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {formData.photos.map(photo => (
                      <div key={photo.id} className="relative aspect-square rounded-xl overflow-hidden border border-white/10 group">
                        <Image src={photo.dataUrl} alt={photo.label} fill className="object-cover" />
                        <button
                          onClick={() => removePhoto(photo.id)}
                          className="absolute top-2 right-2 p-1.5 bg-black/70 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/80"
                        >
                          <TrashIcon className="w-4 h-4 text-white" />
                        </button>
                      </div>
                    ))}
                    {formData.photos.length < 8 && (
                      <button
                        onClick={() => photoInputRef.current?.click()}
                        className="aspect-square rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all flex flex-col items-center justify-center gap-2"
                      >
                        <PlusIcon className="w-8 h-8 text-slate-500" />
                        <span className="text-xs text-slate-400">{language === "en" ? "Add" : "Aggiungi"}</span>
                      </button>
                    )}
                  </div>
                  <input ref={photoInputRef} type="file" accept="image/*" multiple onChange={handlePhotoUpload} className="hidden" />
                  <p className="text-xs text-slate-500 mt-2">{language === "en" ? "If you don't upload photos, AI will use professional stock images." : "Se non carichi foto, l'AI user\u00E0 immagini professionali di stock."}</p>
                </div>

                {/* --- AI Image Generation Toggle --- */}
                <div className="pt-4 border-t border-white/10">
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

                {/* --- Review Compatto + Genera --- */}
                <div className="pt-6 border-t border-white/10 space-y-4">
                  <h3 className="font-medium text-lg flex items-center gap-2">
                    <CheckIcon className="w-5 h-5 text-emerald-400" />
                    {language === "en" ? "Summary" : "Riepilogo"}
                  </h3>
                  <div className="grid sm:grid-cols-2 gap-3 text-sm">
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">Business:</span>{" "}
                      <span className="text-white">{formData.businessName || "—"}</span>
                    </div>
                    {formData.tagline && (
                      <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                        <span className="text-slate-500">Slogan:</span>{" "}
                        <span className="text-white">{formData.tagline}</span>
                      </div>
                    )}
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">Sezioni:</span>{" "}
                      <span className="text-white">{formData.selectedSections.length}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-slate-500">CTA:</span>{" "}
                      <span className="text-white">{CTA_OPTIONS.find(c => c.id === formData.primaryCta)?.label}</span>
                    </div>
                    {selectedStyle && (
                      <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                        <span className="text-slate-500">Template:</span>
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: selectedStyle.primaryColor }} />
                        <span className="text-white">{selectedStyle.label}</span>
                      </div>
                    )}
                    {formData.preferredStyle && !selectedStyle && (
                      <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                        <span className="text-slate-500">Stile:</span>{" "}
                        <span className="text-white">{STYLE_OPTIONS.find(s => s.id === formData.preferredStyle)?.label}</span>
                      </div>
                    )}
                    {formData.photos.length > 0 && (
                      <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                        <span className="text-slate-500">Foto:</span>{" "}
                        <span className="text-white">{formData.photos.length}</span>
                      </div>
                    )}
                    {formData.logo && (
                      <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                        <span className="text-slate-500">Logo:</span>
                        <div className="w-6 h-6 rounded overflow-hidden relative"><Image src={formData.logo} alt="Logo" fill className="object-contain" /></div>
                      </div>
                    )}
                    <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2">
                      <span className="text-slate-500">{language === "en" ? "AI Images:" : "Immagini AI:"}</span>
                      <span className={formData.generateImages ? "text-violet-400" : "text-slate-400"}>
                        {formData.generateImages ? (language === "en" ? "Yes" : "Si") : "No"}
                      </span>
                    </div>
                  </div>

                  {isGenerating ? (
                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
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
                        {language === "en" ? "4-step AI pipeline — Estimated time: 40-60 seconds" : "Pipeline AI a 4 step — Tempo stimato: 40-60 secondi"}
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
                        {isUpgrading ? (language === "en" ? "Activating..." : "Attivazione...") : "Upgrade (DEMO)"}
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
