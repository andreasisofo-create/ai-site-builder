"use client";

export const dynamic = "force-dynamic";
import { useState, useRef } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckIcon,
  CloudArrowUpIcon,
  SparklesIcon,
  BuildingStorefrontIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  GlobeAltIcon,
  PhotoIcon,
  XMarkIcon,
  LightBulbIcon,
  ChevronRightIcon,
  RocketLaunchIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { createSite, generateWebsite, updateSite, generateSlug, CreateSiteData, getQuota, upgradeToPremium } from "@/lib/api";

const STEPS = [
  { id: 1, title: "Brand", icon: BuildingStorefrontIcon },
  { id: 2, title: "Stile", icon: PaintBrushIcon },
  { id: 3, title: "Contenuti", icon: DocumentTextIcon },
  { id: 4, title: "Review", icon: CheckIcon },
];

const SECTIONS = [
  { id: "hero", label: "Hero (Header principale)", default: true },
  { id: "about", label: "Chi Siamo / About", default: true },
  { id: "services", label: "Servizi / Prodotti", default: true },
  { id: "gallery", label: "Galleria", default: false },
  { id: "testimonials", label: "Testimonianze", default: false },
  { id: "team", label: "Team", default: false },
  { id: "contact", label: "Contatti / Form", default: true },
  { id: "footer", label: "Footer completo", default: true },
];

const STYLES = [
  { id: "modern", label: "Moderno & Minimal", description: "Linee pulite, spazi bianchi, elegante", color: "from-slate-600 to-slate-700" },
  { id: "bold", label: "Bold & Creativo", description: "Colori vivaci, animazioni, impatto visivo", color: "from-violet-600 to-purple-700" },
  { id: "classic", label: "Classico & Elegante", description: "Tradizionale, serif, raffinato", color: "from-amber-700 to-orange-800" },
  { id: "corporate", label: "Corporate", description: "Professionale, affidabile, business", color: "from-blue-700 to-indigo-800" },
  { id: "cozy", label: "Cozy & Warm", description: "Accogliente, toni caldi, personale", color: "from-rose-600 to-pink-700" },
];

const COLORS = [
  { id: "blue", label: "Blu", hex: "#3b82f6", class: "bg-blue-500" },
  { id: "violet", label: "Viola", hex: "#8b5cf6", class: "bg-violet-500" },
  { id: "emerald", label: "Verde", hex: "#10b981", class: "bg-emerald-500" },
  { id: "rose", label: "Rosa", hex: "#f43f5e", class: "bg-rose-500" },
  { id: "amber", label: "Ambra", hex: "#f59e0b", class: "bg-amber-500" },
  { id: "slate", label: "Grigio", hex: "#64748b", class: "bg-slate-500" },
];

export default function NewProjectPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSiteId, setCreatedSiteId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [formData, setFormData] = useState({
    businessName: "",
    tagline: "",
    description: "",
    logo: null as string | null,
    referenceImage: null as string | null,
    style: "modern",
    primaryColor: "blue",
    sections: SECTIONS.filter((s) => s.default).map((s) => s.id),
    contactInfo: {
      address: "",
      phone: "",
      email: "",
    },
  });

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData((prev) => ({ ...prev, logo: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleReferenceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData((prev) => ({ ...prev, referenceImage: reader.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  const toggleSection = (sectionId: string) => {
    setFormData((prev) => ({
      ...prev,
      sections: prev.sections.includes(sectionId)
        ? prev.sections.filter((s) => s !== sectionId)
        : [...prev.sections, sectionId],
    }));
  };

  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState(false);

  const handleGenerate = async () => {
    if (!formData.businessName.trim()) {
      toast.error("Inserisci il nome del business");
      return;
    }

    setIsGenerating(true);

    try {
      // Step 1: Verifica quota prima di iniziare
      toast.loading("Verifica quota...", { id: "check" });
      const quota = await getQuota();

      if (!quota.has_remaining_generations) {
        toast.dismiss("check");
        setShowUpgradeModal(true);
        setIsGenerating(false);
        return;
      }
      toast.dismiss("check");

      // Step 2: Crea il sito sul backend
      toast.loading("Creazione progetto...", { id: "create" });

      const siteData: CreateSiteData = {
        name: formData.businessName,
        slug: generateSlug(formData.businessName),
        description: formData.description,
      };

      const site = await createSite(siteData);
      setCreatedSiteId(site.id);
      toast.success("Progetto creato!", { id: "create" });

      // Step 3: Aggiorna stato a "generating"
      await updateSite(site.id, { status: "generating" });

      // Step 4: Chiama l'AI per generare il sito
      toast.loading("Generazione sito con AI... (60-90s)", { id: "generate" });

      const colorHex = COLORS.find(c => c.id === formData.primaryColor)?.hex;

      const generateResult = await generateWebsite({
        business_name: formData.businessName,
        business_description: formData.description + (formData.tagline ? ` - ${formData.tagline}` : ""),
        sections: formData.sections,
        style_preferences: {
          primary_color: colorHex,
          mood: STYLES.find(s => s.id === formData.style)?.label,
        },
        logo_url: formData.logo || undefined,
        reference_analysis: formData.referenceImage || undefined,
      });

      if (!generateResult.success || !generateResult.html_content) {
        throw new Error(generateResult.error || "Errore nella generazione");
      }

      // Step 5: Salva l'HTML generato
      await updateSite(site.id, {
        html_content: generateResult.html_content,
        status: "ready",
        thumbnail: `https://placehold.co/600x400/1a1a1a/666?text=${encodeURIComponent(formData.businessName)}`,
      });

      // Mostra messaggio con generazioni rimanenti
      const remaining = generateResult.quota?.remaining_generations;
      if (remaining !== undefined && remaining > 0) {
        toast.success(`Sito generato! Ti rimangono ${remaining} generazioni`, { id: "generate" });
      } else if (remaining === 0) {
        toast.success("Sito generato! Hai esaurito le generazioni gratuite", { id: "generate" });
      } else {
        toast.success("Sito generato con successo!", { id: "generate" });
      }

      // Redirect all'editor
      router.push(`/editor/${site.id}`);

    } catch (error: any) {
      // Gestione errore quota specifico
      if (error.isQuotaError || error.quota?.upgrade_required) {
        setShowUpgradeModal(true);
      } else {
        toast.error(error.message || "Errore nella generazione", { id: "generate" });
      }
      setIsGenerating(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      setIsUpgrading(true);
      await upgradeToPremium();
      toast.success("Upgrade completato! Ora hai generazioni illimitate");
      setShowUpgradeModal(false);
      // Riprova la generazione
      handleGenerate();
    } catch (error: any) {
      toast.error(error.message || "Errore nell'upgrade");
    } finally {
      setIsUpgrading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.businessName.trim() && formData.description.trim();
      case 2:
        return true;
      case 3:
        return formData.sections.length > 0;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/5 z-50">
        <div className="h-full max-w-7xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/dashboard")}
              className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                <SparklesIcon className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold">Nuovo Progetto</span>
            </div>
          </div>

          {/* Steps Indicator */}
          <div className="hidden md:flex items-center gap-2">
            {STEPS.map((step, idx) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition-all ${currentStep === step.id
                    ? "bg-white/10 text-white"
                    : currentStep > step.id
                      ? "text-emerald-400"
                      : "text-slate-500"
                    }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${currentStep === step.id
                      ? "bg-blue-500 text-white"
                      : currentStep > step.id
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-white/5 text-slate-500"
                      }`}
                  >
                    {currentStep > step.id ? <CheckIcon className="w-3 h-3" /> : step.id}
                  </div>
                  <span className="text-sm font-medium">{step.title}</span>
                </div>
                {idx < STEPS.length - 1 && (
                  <ChevronRightIcon className="w-4 h-4 text-slate-600 mx-1" />
                )}
              </div>
            ))}
          </div>

          <div className="w-20" /> {/* Spacer for alignment */}
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 pb-32 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Step 1: Brand & Info */}
          {currentStep === 1 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Informazioni del Brand</h1>
                <p className="text-slate-400">Raccontaci del tuo business per personalizzare il sito</p>
              </div>

              <div className="space-y-6">
                {/* Business Name */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Nome del Business <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.businessName}
                    onChange={(e) => setFormData((prev) => ({ ...prev, businessName: e.target.value }))}
                    placeholder="es. Ristorante Da Mario"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.07] transition-all"
                  />
                </div>

                {/* Tagline */}
                <div>
                  <label className="block text-sm font-medium mb-2">Slogan / Tagline</label>
                  <input
                    type="text"
                    value={formData.tagline}
                    onChange={(e) => setFormData((prev) => ({ ...prev, tagline: e.target.value }))}
                    placeholder="es. Il vero gusto della tradizione"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.07] transition-all"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Descrizione dell&apos;attività <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                    placeholder="Descrivi cosa fai, i tuoi servizi, la tua storia..."
                    rows={4}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.07] transition-all resize-none"
                  />
                  <p className="text-xs text-slate-500 mt-2">
                    Suggerimento: Più dettagli fornisci, migliore sarà il risultato dell&apos;AI
                  </p>
                </div>

                {/* Logo Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">Logo (opzionale)</label>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="relative aspect-video max-w-sm rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer flex flex-col items-center justify-center gap-3"
                  >
                    {formData.logo ? (
                      <Image
                        src={formData.logo}
                        alt="Logo"
                        fill
                        className="object-contain p-4"
                      />
                    ) : (
                      <>
                        <CloudArrowUpIcon className="w-10 h-10 text-slate-500" />
                        <div className="text-center">
                          <p className="text-sm text-slate-400">Clicca per caricare il logo</p>
                          <p className="text-xs text-slate-600 mt-1">PNG, JPG o SVG (max 2MB)</p>
                        </div>
                      </>
                    )}
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Style */}
          {currentStep === 2 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Stile e Design</h1>
                <p className="text-slate-400">Scegli lo stile che meglio rappresenta il tuo brand</p>
              </div>

              {/* Style Selection */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-4">Stile del sito</label>
                  <div className="grid sm:grid-cols-2 gap-4">
                    {STYLES.map((style) => (
                      <button
                        key={style.id}
                        onClick={() => setFormData((prev) => ({ ...prev, style: style.id }))}
                        className={`p-4 rounded-xl border transition-all text-left ${formData.style === style.id
                          ? "border-blue-500 bg-blue-500/10"
                          : "border-white/10 bg-white/[0.02] hover:border-white/20"
                          }`}
                      >
                        <div className={`w-full h-20 rounded-lg bg-gradient-to-br ${style.color} mb-3`} />
                        <h4 className="font-medium mb-1">{style.label}</h4>
                        <p className="text-sm text-slate-400">{style.description}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Color Selection */}
                <div>
                  <label className="block text-sm font-medium mb-4">Colore primario</label>
                  <div className="flex flex-wrap gap-3">
                    {COLORS.map((color) => (
                      <button
                        key={color.id}
                        onClick={() => setFormData((prev) => ({ ...prev, primaryColor: color.id }))}
                        className={`group relative w-16 h-16 rounded-xl ${color.class} transition-all ${formData.primaryColor === color.id
                          ? "ring-2 ring-white ring-offset-2 ring-offset-[#0a0a0a] scale-110"
                          : "hover:scale-105"
                          }`}
                      >
                        {formData.primaryColor === color.id && (
                          <CheckIcon className="absolute inset-0 m-auto w-6 h-6 text-white" />
                        )}
                        <span className="sr-only">{color.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Reference Image */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Immagine di riferimento (opzionale)
                  </label>
                  <p className="text-sm text-slate-500 mb-4">
                    Carica uno screenshot di un sito che ti piace per ispirare l&apos;AI
                  </p>
                  <div
                    onClick={() => document.getElementById("reference-upload")?.click()}
                    className={`relative aspect-video max-w-lg rounded-xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center gap-3 ${formData.referenceImage
                      ? "border-blue-500/50 bg-blue-500/5"
                      : "border-white/10 hover:border-white/30 bg-white/[0.02]"
                      }`}
                  >
                    {formData.referenceImage ? (
                      <>
                        <Image
                          src={formData.referenceImage}
                          alt="Reference"
                          fill
                          className="object-cover rounded-xl"
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setFormData((prev) => ({ ...prev, referenceImage: null }));
                          }}
                          className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-lg hover:bg-black/80 transition-colors"
                        >
                          <XMarkIcon className="w-4 h-4" />
                        </button>
                      </>
                    ) : (
                      <>
                        <PhotoIcon className="w-10 h-10 text-slate-500" />
                        <div className="text-center">
                          <p className="text-sm text-slate-400">Carica immagine di riferimento</p>
                          <p className="text-xs text-slate-600 mt-1">Screenshot di siti che ti ispirano</p>
                        </div>
                      </>
                    )}
                  </div>
                  <input
                    id="reference-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleReferenceUpload}
                    className="hidden"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Content */}
          {currentStep === 3 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Contenuti</h1>
                <p className="text-slate-400">Seleziona le sezioni da includere nel tuo sito</p>
              </div>

              <div className="space-y-6">
                {/* Sections */}
                <div>
                  <label className="block text-sm font-medium mb-4">Sezioni del sito</label>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {SECTIONS.map((section) => (
                      <button
                        key={section.id}
                        onClick={() => toggleSection(section.id)}
                        className={`flex items-center gap-3 p-4 rounded-xl border transition-all text-left ${formData.sections.includes(section.id)
                          ? "border-blue-500/50 bg-blue-500/10"
                          : "border-white/10 bg-white/[0.02] hover:border-white/20"
                          }`}
                      >
                        <div
                          className={`w-5 h-5 rounded border flex items-center justify-center transition-all ${formData.sections.includes(section.id)
                            ? "bg-blue-500 border-blue-500"
                            : "border-white/30"
                            }`}
                        >
                          {formData.sections.includes(section.id) && <CheckIcon className="w-3.5 h-3.5 text-white" />}
                        </div>
                        <span className="flex-1">{section.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Contact Info */}
                <div className="pt-6 border-t border-white/10">
                  <label className="block text-sm font-medium mb-4">Informazioni di contatto</label>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs text-slate-500 mb-1.5">Indirizzo</label>
                      <input
                        type="text"
                        value={formData.contactInfo.address}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            contactInfo: { ...prev.contactInfo, address: e.target.value },
                          }))
                        }
                        placeholder="Via Roma 123, 00100 Roma"
                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                      />
                    </div>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1.5">Telefono</label>
                        <input
                          type="tel"
                          value={formData.contactInfo.phone}
                          onChange={(e) =>
                            setFormData((prev) => ({
                              ...prev,
                              contactInfo: { ...prev.contactInfo, phone: e.target.value },
                            }))
                          }
                          placeholder="+39 123 456 7890"
                          className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-slate-500 mb-1.5">Email</label>
                        <input
                          type="email"
                          value={formData.contactInfo.email}
                          onChange={(e) =>
                            setFormData((prev) => ({
                              ...prev,
                              contactInfo: { ...prev.contactInfo, email: e.target.value },
                            }))
                          }
                          placeholder="info@esempio.com"
                          className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 transition-all"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {currentStep === 4 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Review & Genera</h1>
                <p className="text-slate-400">Controlla le informazioni prima di generare il sito</p>
              </div>

              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                  <h3 className="font-medium mb-4 flex items-center gap-2">
                    <BuildingStorefrontIcon className="w-5 h-5 text-blue-400" />
                    Brand
                  </h3>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Nome</span>
                      <span className="text-white">{formData.businessName}</span>
                    </div>
                    {formData.tagline && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Tagline</span>
                        <span className="text-white">{formData.tagline}</span>
                      </div>
                    )}
                  </dl>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                  <h3 className="font-medium mb-4 flex items-center gap-2">
                    <PaintBrushIcon className="w-5 h-5 text-violet-400" />
                    Stile
                  </h3>
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-12 h-12 rounded-lg ${COLORS.find((c) => c.id === formData.primaryColor)?.class
                        }`}
                    />
                    <div>
                      <p className="font-medium">
                        {STYLES.find((s) => s.id === formData.style)?.label}
                      </p>
                      <p className="text-sm text-slate-500">
                        {COLORS.find((c) => c.id === formData.primaryColor)?.label}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                  <h3 className="font-medium mb-4 flex items-center gap-2">
                    <DocumentTextIcon className="w-5 h-5 text-emerald-400" />
                    Sezioni ({formData.sections.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {formData.sections.map((sectionId) => (
                      <span
                        key={sectionId}
                        className="px-3 py-1 rounded-full bg-white/5 text-sm text-slate-300"
                      >
                        {SECTIONS.find((s) => s.id === sectionId)?.label}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full py-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl font-semibold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-3 disabled:opacity-70"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Generazione in corso...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-5 h-5" />
                      Genera il Mio Sito
                    </>
                  )}
                </button>

                <p className="text-center text-sm text-slate-500">
                  Tempo stimato: 60-90 secondi
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer Navigation */}
      <footer className="fixed bottom-0 left-0 right-0 h-20 bg-[#0a0a0a]/95 backdrop-blur-xl border-t border-white/5">
        <div className="h-full max-w-7xl mx-auto px-6 flex items-center justify-between">
          <button
            onClick={() => setCurrentStep((prev) => Math.max(1, prev - 1))}
            disabled={currentStep === 1 || isGenerating}
            className="flex items-center gap-2 px-6 py-2.5 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Indietro
          </button>

          {/* Mobile Step Indicator */}
          <div className="md:hidden text-sm text-slate-400">
            Passo {currentStep} di {STEPS.length}
          </div>

          <button
            onClick={() => {
              if (currentStep === STEPS.length) {
                handleGenerate();
              } else {
                setCurrentStep((prev) => Math.min(STEPS.length, prev + 1));
              }
            }}
            disabled={!canProceed() || isGenerating}
            className="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-full font-medium transition-all"
          >
            {currentStep === STEPS.length ? "Genera" : "Avanti"}
            <ArrowRightIcon className="w-4 h-4" />
          </button>
        </div>
      </footer>

      {/* Upgrade Modal */}
      <Transition appear show={showUpgradeModal} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setShowUpgradeModal(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/80" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-[#111] border border-white/10 p-6 text-left align-middle shadow-xl transition-all">
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
                      <SparklesIcon className="w-8 h-8 text-white" />
                    </div>

                    <Dialog.Title as="h3" className="text-xl font-semibold mb-2">
                      Hai esaurito le generazioni gratuite
                    </Dialog.Title>

                    <p className="text-slate-400 mb-6">
                      Hai usato tutte le tue 2 generazioni di test.
                      Passa a Premium per generazioni illimitate.
                    </p>

                    <div className="bg-white/5 rounded-xl p-4 mb-6">
                      <div className="flex items-center justify-center gap-2 text-amber-400 mb-2">
                        <SparklesIcon className="w-5 h-5" />
                        <span className="font-semibold">Piano Premium</span>
                      </div>
                      <ul className="text-sm text-slate-400 space-y-1">
                        <li>✓ Generazioni illimitate</li>
                        <li>✓ Esporta codice sorgente</li>
                        <li>✓ Supporto prioritario</li>
                        <li>✓ Nessuna filigrana</li>
                      </ul>
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowUpgradeModal(false)}
                        className="flex-1 px-4 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                      >
                        Più tardi
                      </button>
                      <button
                        onClick={handleUpgrade}
                        disabled={isUpgrading}
                        className="flex-1 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 rounded-lg font-medium transition-all disabled:opacity-50"
                      >
                        {isUpgrading ? "Attivazione..." : "Attiva Premium (DEMO)"}
                      </button>
                    </div>

                    <p className="text-xs text-slate-500 mt-4">
                      DEMO: In produzione qui ci sarà il checkout Stripe
                    </p>
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
