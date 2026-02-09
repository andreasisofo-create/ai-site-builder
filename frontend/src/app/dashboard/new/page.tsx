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

// ============ TEMPLATE DATA ============

export interface TemplateStyle {
  id: string;
  label: string;
  description: string;
  image: string;
  mood: string;
  primaryColor: string;
  secondaryColor: string;
  sections: string[];
}

export interface TemplateCategory {
  id: string;
  label: string;
  description: string;
  icon: string;
  image: string;
  styles: TemplateStyle[];
}

export const TEMPLATE_CATEGORIES: TemplateCategory[] = [
  {
    id: "restaurant",
    label: "Ristorante & Food",
    description: "Ristoranti, bar, pizzerie, pasticcerie",
    icon: "🍽️",
    image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&h=400&fit=crop",
    styles: [
      {
        id: "restaurant-elegant",
        label: "Elegante & Raffinato",
        description: "Atmosfera sofisticata per ristoranti di classe",
        image: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&h=400&fit=crop",
        mood: "elegant",
        primaryColor: "#b8860b",
        secondaryColor: "#1a1a2e",
        sections: ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
      },
      {
        id: "restaurant-cozy",
        label: "Accogliente & Tradizionale",
        description: "Calore e tradizione per trattorie e osterie",
        image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&h=400&fit=crop",
        mood: "cozy",
        primaryColor: "#c0392b",
        secondaryColor: "#f5e6d3",
        sections: ["hero", "about", "services", "testimonials", "contact", "footer"],
      },
      {
        id: "restaurant-modern",
        label: "Moderno & Minimal",
        description: "Design pulito per locali contemporanei",
        image: "https://images.unsplash.com/photo-1550966871-3ed3cdb51f3a?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#2d3436",
        secondaryColor: "#00b894",
        sections: ["hero", "about", "services", "gallery", "contact", "footer"],
      },
    ],
  },
  {
    id: "agency",
    label: "Agenzia & Startup",
    description: "Agenzie digitali, startup tech, consulenza",
    icon: "🚀",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
    styles: [
      {
        id: "agency-bold",
        label: "Bold & Dinamico",
        description: "Impatto visivo forte per brand innovativi",
        image: "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#6c5ce7",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "services", "features", "testimonials", "cta", "contact", "footer"],
      },
      {
        id: "agency-clean",
        label: "Pulito & Professionale",
        description: "Minimalismo corporate per aziende tech",
        image: "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#0984e3",
        secondaryColor: "#dfe6e9",
        sections: ["hero", "about", "services", "features", "cta", "contact", "footer"],
      },
      {
        id: "agency-dark",
        label: "Dark & Premium",
        description: "Tema scuro per agenzie creative",
        image: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#00cec9",
        secondaryColor: "#636e72",
        sections: ["hero", "about", "services", "features", "testimonials", "contact", "footer"],
      },
    ],
  },
  {
    id: "portfolio",
    label: "Portfolio & Creativo",
    description: "Fotografi, designer, artisti, freelancer",
    icon: "🎨",
    image: "https://images.unsplash.com/photo-1545235617-9465d2a55698?w=600&h=400&fit=crop",
    styles: [
      {
        id: "portfolio-gallery",
        label: "Galleria Immersiva",
        description: "Focus sulle immagini, layout a griglia",
        image: "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#2d3436",
        secondaryColor: "#fdcb6e",
        sections: ["hero", "about", "gallery", "services", "testimonials", "contact", "footer"],
      },
      {
        id: "portfolio-minimal",
        label: "Minimal & Tipografico",
        description: "Spazi bianchi, focus sul contenuto",
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#0c0c0c",
        secondaryColor: "#e17055",
        sections: ["hero", "about", "gallery", "contact", "footer"],
      },
      {
        id: "portfolio-creative",
        label: "Creativo & Colorato",
        description: "Colori vivaci per artisti e designer",
        image: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop",
        mood: "bold",
        primaryColor: "#e84393",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "gallery", "services", "contact", "footer"],
      },
    ],
  },
  {
    id: "business",
    label: "Business & Professionale",
    description: "Studi legali, medici, consulenti, PMI",
    icon: "💼",
    image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&h=400&fit=crop",
    styles: [
      {
        id: "business-corporate",
        label: "Corporate Classico",
        description: "Professionale e affidabile",
        image: "https://images.unsplash.com/photo-1507679799987-c73b1057bffc?w=600&h=400&fit=crop",
        mood: "corporate",
        primaryColor: "#2c3e50",
        secondaryColor: "#3498db",
        sections: ["hero", "about", "services", "features", "testimonials", "contact", "footer"],
      },
      {
        id: "business-trust",
        label: "Trust & Autorità",
        description: "Per studi legali, medici, finanza",
        image: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop",
        mood: "classic",
        primaryColor: "#1a3c5e",
        secondaryColor: "#c5a04b",
        sections: ["hero", "about", "services", "team", "testimonials", "contact", "footer"],
      },
      {
        id: "business-fresh",
        label: "Fresco & Moderno",
        description: "PMI innovative e consulenti tech",
        image: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop",
        mood: "modern",
        primaryColor: "#00b894",
        secondaryColor: "#0984e3",
        sections: ["hero", "about", "services", "features", "cta", "contact", "footer"],
      },
    ],
  },
];

// ============ SECTION LABELS ============
const SECTION_LABELS: Record<string, string> = {
  hero: "Hero (Header principale)",
  about: "Chi Siamo / About",
  services: "Servizi / Prodotti",
  gallery: "Galleria",
  testimonials: "Testimonianze",
  team: "Team",
  features: "Funzionalità",
  cta: "Call to Action",
  contact: "Contatti / Form",
  footer: "Footer completo",
};

// ============ PREVIEW GENERATOR ============

function generateStylePreviewHtml(style: TemplateStyle, categoryLabel: string): string {
  const p = style.primaryColor;
  const s = style.secondaryColor;
  const isDark = style.mood === "bold" || style.mood === "elegant" || style.mood === "corporate" || style.mood === "classic";
  const bg = isDark ? "#0f0f0f" : "#ffffff";
  const text = isDark ? "#ffffff" : "#1a1a1a";
  const muted = isDark ? "#999999" : "#666666";
  const cardBg = isDark ? "#1a1a1a" : "#f5f5f5";

  const sectionHtml: Record<string, string> = {
    hero: `
      <section style="min-height:60vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 40px;background:linear-gradient(135deg,${p}22,${s}22);position:relative;overflow:hidden">
        <div style="position:absolute;top:-50%;right:-20%;width:500px;height:500px;border-radius:50%;background:${p}15"></div>
        <div style="position:relative;z-index:1;max-width:700px">
          <div style="display:inline-block;padding:6px 16px;border-radius:20px;background:${p}20;color:${p};font-size:13px;margin-bottom:20px">${categoryLabel}</div>
          <h1 style="font-size:clamp(32px,5vw,56px);font-weight:800;margin:0 0 16px;color:${text};line-height:1.1">Il Tuo Sito<br><span style="color:${p}">Professionale</span></h1>
          <p style="color:${muted};font-size:18px;margin:0 0 32px;max-width:500px;margin-left:auto;margin-right:auto">Creato con AI - Design ${style.label}</p>
          <div style="display:flex;gap:12px;justify-content:center">
            <a style="padding:14px 32px;background:${p};color:white;border-radius:12px;font-weight:600;text-decoration:none;font-size:15px">Scopri di piu</a>
            <a style="padding:14px 32px;background:${isDark ? '#ffffff15' : '#00000008'};color:${text};border-radius:12px;font-weight:600;text-decoration:none;font-size:15px;border:1px solid ${isDark ? '#ffffff20' : '#00000015'}">Contattaci</a>
          </div>
        </div>
      </section>`,
    about: `
      <section style="padding:80px 40px;background:${bg}">
        <div style="max-width:900px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center">
          <div>
            <div style="font-size:12px;text-transform:uppercase;letter-spacing:3px;color:${p};margin-bottom:12px;font-weight:600">Chi Siamo</div>
            <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 16px">La nostra storia</h2>
            <p style="color:${muted};line-height:1.8;font-size:15px">Offriamo servizi di qualita con passione e dedizione. La nostra esperienza ci permette di garantire risultati eccellenti per ogni cliente.</p>
          </div>
          <div style="aspect-ratio:4/3;background:linear-gradient(135deg,${p}30,${s}30);border-radius:16px"></div>
        </div>
      </section>`,
    services: `
      <section style="padding:80px 40px;background:${cardBg}">
        <div style="max-width:900px;margin:0 auto;text-align:center">
          <div style="font-size:12px;text-transform:uppercase;letter-spacing:3px;color:${p};margin-bottom:12px;font-weight:600">Servizi</div>
          <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 48px">Cosa offriamo</h2>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">
            ${[1,2,3].map(i => `
              <div style="background:${bg};padding:32px 24px;border-radius:16px;text-align:center;border:1px solid ${isDark ? '#ffffff10' : '#00000008'}">
                <div style="width:56px;height:56px;border-radius:14px;background:${p}15;margin:0 auto 16px;display:flex;align-items:center;justify-content:center">
                  <div style="width:24px;height:24px;border-radius:6px;background:${p}"></div>
                </div>
                <h3 style="font-size:17px;font-weight:600;color:${text};margin:0 0 8px">Servizio ${i}</h3>
                <p style="color:${muted};font-size:14px;line-height:1.6;margin:0">Descrizione del servizio offerto ai nostri clienti</p>
              </div>
            `).join("")}
          </div>
        </div>
      </section>`,
    gallery: `
      <section style="padding:80px 40px;background:${bg}">
        <div style="max-width:900px;margin:0 auto;text-align:center">
          <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 48px">Galleria</h2>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
            ${[1,2,3,4,5,6].map(i => `
              <div style="aspect-ratio:1;border-radius:12px;background:linear-gradient(${i*45}deg,${p}${20+i*5},${s}${20+i*5})"></div>
            `).join("")}
          </div>
        </div>
      </section>`,
    testimonials: `
      <section style="padding:80px 40px;background:${cardBg}">
        <div style="max-width:900px;margin:0 auto;text-align:center">
          <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 48px">Testimonianze</h2>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:24px">
            ${[1,2].map(() => `
              <div style="background:${bg};padding:32px;border-radius:16px;text-align:left;border:1px solid ${isDark ? '#ffffff10' : '#00000008'}">
                <div style="color:${p};font-size:32px;margin-bottom:12px">&ldquo;</div>
                <p style="color:${muted};font-size:15px;line-height:1.7;margin:0 0 20px">Servizio eccellente, professionalita e risultati oltre le aspettative.</p>
                <div style="display:flex;align-items:center;gap:12px">
                  <div style="width:40px;height:40px;border-radius:50%;background:${p}20"></div>
                  <div><div style="font-weight:600;color:${text};font-size:14px">Cliente Soddisfatto</div><div style="color:${muted};font-size:12px">Azienda</div></div>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      </section>`,
    features: `
      <section style="padding:80px 40px;background:${bg}">
        <div style="max-width:900px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center">
          <div>
            <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 24px">Perche sceglierci</h2>
            ${[1,2,3].map(i => `
              <div style="display:flex;gap:16px;margin-bottom:20px">
                <div style="width:40px;height:40px;border-radius:10px;background:${p}15;flex-shrink:0;display:flex;align-items:center;justify-content:center">
                  <div style="width:16px;height:16px;border-radius:4px;background:${p}"></div>
                </div>
                <div><h4 style="font-size:15px;font-weight:600;color:${text};margin:0 0 4px">Vantaggio ${i}</h4><p style="color:${muted};font-size:14px;margin:0">Breve descrizione del vantaggio offerto</p></div>
              </div>
            `).join("")}
          </div>
          <div style="aspect-ratio:1;background:linear-gradient(135deg,${p}20,${s}20);border-radius:16px"></div>
        </div>
      </section>`,
    team: `
      <section style="padding:80px 40px;background:${bg}">
        <div style="max-width:900px;margin:0 auto;text-align:center">
          <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 48px">Il Nostro Team</h2>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">
            ${[1,2,3].map(i => `
              <div style="text-align:center">
                <div style="width:100px;height:100px;border-radius:50%;background:${p}15;margin:0 auto 16px"></div>
                <h4 style="font-size:16px;font-weight:600;color:${text};margin:0 0 4px">Membro ${i}</h4>
                <p style="color:${muted};font-size:13px;margin:0">Ruolo professionale</p>
              </div>
            `).join("")}
          </div>
        </div>
      </section>`,
    cta: `
      <section style="padding:80px 40px;background:linear-gradient(135deg,${p},${s});text-align:center;border-radius:0">
        <div style="max-width:600px;margin:0 auto">
          <h2 style="font-size:36px;font-weight:700;color:white;margin:0 0 16px">Pronto per iniziare?</h2>
          <p style="color:rgba(255,255,255,0.8);font-size:18px;margin:0 0 32px">Contattaci oggi per una consulenza gratuita</p>
          <a style="display:inline-block;padding:16px 40px;background:white;color:${p};border-radius:12px;font-weight:700;text-decoration:none;font-size:16px">Contattaci Ora</a>
        </div>
      </section>`,
    contact: `
      <section style="padding:80px 40px;background:${cardBg}">
        <div style="max-width:600px;margin:0 auto;text-align:center">
          <h2 style="font-size:32px;font-weight:700;color:${text};margin:0 0 48px">Contattaci</h2>
          <div style="display:flex;flex-direction:column;gap:16px">
            <div style="padding:16px;background:${bg};border-radius:12px;border:1px solid ${isDark ? '#ffffff15' : '#00000010'};color:${muted};text-align:left;font-size:14px">Nome e cognome</div>
            <div style="padding:16px;background:${bg};border-radius:12px;border:1px solid ${isDark ? '#ffffff15' : '#00000010'};color:${muted};text-align:left;font-size:14px">Email</div>
            <div style="padding:16px 16px 60px;background:${bg};border-radius:12px;border:1px solid ${isDark ? '#ffffff15' : '#00000010'};color:${muted};text-align:left;font-size:14px">Messaggio</div>
            <button style="padding:16px;background:${p};color:white;border:none;border-radius:12px;font-weight:600;font-size:15px;cursor:pointer">Invia Messaggio</button>
          </div>
        </div>
      </section>`,
    footer: `
      <footer style="padding:40px;background:${isDark ? '#080808' : '#1a1a1a'};text-align:center">
        <p style="color:#666;font-size:13px;margin:0">&copy; 2025 La Tua Azienda. Tutti i diritti riservati.</p>
      </footer>`,
  };

  const body = style.sections.map(sec => sectionHtml[sec] || "").join("");

  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:${bg};color:${text};overflow-x:hidden}img{max-width:100%}a{text-decoration:none}</style></head><body>${body}</body></html>`;
}

// ============ COMPONENT ============

function NewProjectContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const templateParam = searchParams.get("template");

  // Find pre-selected category if coming from dashboard
  const initialCategory = TEMPLATE_CATEGORIES.find(c => c.id === templateParam) || null;

  const [currentStep, setCurrentStep] = useState(initialCategory ? 1 : 0);
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | null>(initialCategory);
  const [selectedStyle, setSelectedStyle] = useState<TemplateStyle | null>(initialCategory?.styles[0] || null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [createdSiteId, setCreatedSiteId] = useState<number | null>(null);
  const logoInputRef = useRef<HTMLInputElement>(null);
  const photoInputRef = useRef<HTMLInputElement>(null);

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

  // Steps definition based on whether template is selected
  const WIZARD_STEPS = selectedStyle
    ? [
        { id: 0, title: "Template", icon: PaintBrushIcon },
        { id: 1, title: "Stili", icon: PaintBrushIcon },
        { id: 2, title: "Brand", icon: BuildingStorefrontIcon },
        { id: 3, title: "Foto", icon: PhotoIcon },
        { id: 4, title: "Review", icon: CheckIcon },
      ]
    : [
        { id: 0, title: "Template", icon: PaintBrushIcon },
        { id: 1, title: "Stili", icon: PaintBrushIcon },
        { id: 2, title: "Brand", icon: BuildingStorefrontIcon },
        { id: 3, title: "Foto", icon: PhotoIcon },
        { id: 4, title: "Review", icon: CheckIcon },
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

  // Photo uploads
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      if (formData.photos.length >= 8) {
        toast.error("Massimo 8 foto");
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

  // Select category → go to styles (auto-select first style for preview)
  const selectCategory = (category: TemplateCategory) => {
    setSelectedCategory(category);
    setSelectedStyle(category.styles[0] || null);
    setCurrentStep(1);
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
          setGenerationProgress({ step: 3, totalSteps: 3, message: "Completato!", percentage: 100 });
          toast.success("Sito generato con successo!");
          setTimeout(() => router.push(`/editor/${siteId}`), 1000);
        }
        if (!genStatus.is_generating && genStatus.status === "draft" && genStatus.message) {
          stopProgressPolling();
          setIsGenerating(false);
          toast.error(genStatus.message || "Errore nella generazione");
        }
      } catch { /* ignore */ }
    }, 3000);
  };

  const stopProgressPolling = () => {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
  };

  // Generate
  const handleGenerate = async () => {
    if (!formData.businessName.trim()) {
      toast.error("Inserisci il nome del business");
      return;
    }
    if (!selectedStyle) {
      toast.error("Seleziona un template e uno stile");
      return;
    }

    setIsGenerating(true);
    setPreviewData(null);
    setGenerationProgress({ step: 0, totalSteps: 3, message: "Preparazione...", percentage: 0 });

    try {
      const quota = await getQuota();
      if (!quota.has_remaining_generations) {
        setShowUpgradeModal(true);
        setIsGenerating(false);
        return;
      }

      setGenerationProgress({ step: 0, totalSteps: 3, message: "Creazione progetto...", percentage: 5 });
      const siteData: CreateSiteData = {
        name: formData.businessName,
        slug: generateSlug(formData.businessName),
        description: formData.description,
      };
      const site = await createSite(siteData);
      setCreatedSiteId(site.id);
      startProgressPolling(site.id);

      setGenerationProgress({ step: 1, totalSteps: 3, message: "Avvio generazione AI...", percentage: 10 });

      // Build description with template context
      const templateContext = `Template: ${selectedCategory?.label} - Stile: ${selectedStyle.label}. ${selectedStyle.description}.`;
      const fullDescription = `${templateContext}\n\nDescrizione attività: ${formData.description}${formData.tagline ? `\nSlogan: ${formData.tagline}` : ""}`;

      // Include user photos as additional context
      const photoUrls = formData.photos.map(p => p.dataUrl);

      const generateResult = await generateWebsite({
        business_name: formData.businessName,
        business_description: fullDescription,
        sections: selectedStyle.sections,
        style_preferences: {
          primary_color: selectedStyle.primaryColor,
          secondary_color: selectedStyle.secondaryColor,
          mood: selectedStyle.mood,
        },
        logo_url: formData.logo || undefined,
        reference_image_url: photoUrls.length > 0 ? photoUrls[0] : undefined,
        contact_info: (formData.contactInfo.address || formData.contactInfo.phone || formData.contactInfo.email)
          ? formData.contactInfo : undefined,
        site_id: site.id,
      });

      if (!generateResult.success) throw new Error(generateResult.error || "Errore nell'avvio della generazione");

      await updateSite(site.id, {
        thumbnail: `https://placehold.co/600x400/1a1a1a/666?text=${encodeURIComponent(formData.businessName)}`,
      });

      toast.success("Generazione avviata! Attendere...");
    } catch (error: any) {
      stopProgressPolling();
      if (error.isQuotaError || error.quota?.upgrade_required) {
        setShowUpgradeModal(true);
      } else {
        toast.error(error.message || "Errore nella generazione");
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
      toast.success("Upgrade completato!");
      setShowUpgradeModal(false);
      handleGenerate();
    } catch (error: any) {
      toast.error(error.message || "Errore nell'upgrade");
    } finally {
      setIsUpgrading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: return !!selectedCategory;
      case 1: return !!selectedStyle;
      case 2: return formData.businessName.trim() && formData.description.trim();
      case 3: return true;
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
              <span className="font-semibold">Nuovo Progetto</span>
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

          {/* ===== STEP 0: Scegli Categoria Template ===== */}
          {currentStep === 0 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Scegli il tipo di sito</h1>
                <p className="text-slate-400">Seleziona la categoria che meglio descrive la tua attivit&agrave;</p>
              </div>

              <div className="grid sm:grid-cols-2 gap-6">
                {TEMPLATE_CATEGORIES.map(category => (
                  <button
                    key={category.id}
                    onClick={() => selectCategory(category)}
                    className={`group relative aspect-[4/3] rounded-2xl overflow-hidden border-2 transition-all text-left ${
                      selectedCategory?.id === category.id
                        ? "border-blue-500 shadow-lg shadow-blue-500/20"
                        : "border-white/10 hover:border-white/30"
                    }`}
                  >
                    <Image src={category.image} alt={category.label} fill className="object-cover transition-transform duration-500 group-hover:scale-105" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
                    <div className="absolute inset-0 p-6 flex flex-col justify-end">
                      <div className="text-3xl mb-2">{category.icon}</div>
                      <h3 className="text-xl font-bold text-white mb-1">{category.label}</h3>
                      <p className="text-sm text-slate-300">{category.description}</p>
                    </div>
                    {selectedCategory?.id === category.id && (
                      <div className="absolute top-4 right-4 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                        <CheckIcon className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ===== STEP 1: Scegli Stile ===== */}
          {currentStep === 1 && selectedCategory && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-8">
                <div className="text-4xl mb-3">{selectedCategory.icon}</div>
                <h1 className="text-3xl font-bold mb-3">Scegli lo stile per {selectedCategory.label}</h1>
                <p className="text-slate-400">Clicca su uno stile per vedere l&apos;anteprima del sito</p>
              </div>

              <div className="flex gap-6 h-[70vh]">
                {/* Style selector - left sidebar */}
                <div className="w-72 flex-shrink-0 space-y-3 overflow-y-auto pr-2">
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
                      <div className="p-3 bg-[#111]">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: style.primaryColor }} />
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: style.secondaryColor }} />
                          <span className="text-xs font-medium text-white ml-auto">{style.label}</span>
                        </div>
                        <p className="text-[11px] text-slate-400">{style.description}</p>
                      </div>
                      {selectedStyle?.id === style.id && (
                        <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center">
                          <CheckIcon className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                {/* Preview - main area */}
                <div className="flex-1 rounded-2xl border border-white/10 overflow-hidden bg-[#111] flex flex-col">
                  {selectedStyle ? (
                    <>
                      <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-[#0a0a0a]">
                        <div className="flex gap-1.5">
                          <div className="w-3 h-3 rounded-full bg-red-500/60" />
                          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                          <div className="w-3 h-3 rounded-full bg-green-500/60" />
                        </div>
                        <div className="flex-1 text-center">
                          <div className="inline-block px-4 py-1 rounded-md bg-white/5 text-xs text-slate-400">
                            www.tuosito.it &mdash; {selectedStyle.label}
                          </div>
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
                      <div className="text-center">
                        <PaintBrushIcon className="w-12 h-12 mx-auto mb-3 opacity-40" />
                        <p>Seleziona uno stile per vedere l&apos;anteprima</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 2: Brand Info ===== */}
          {currentStep === 2 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Informazioni del Brand</h1>
                <p className="text-slate-400">Raccontaci del tuo business per personalizzare il sito</p>
              </div>

              <div className="max-w-2xl mx-auto space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Nome del Business <span className="text-red-400">*</span></label>
                  <input
                    type="text"
                    value={formData.businessName}
                    onChange={e => setFormData(prev => ({ ...prev, businessName: e.target.value }))}
                    placeholder="es. Ristorante Da Mario"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Slogan / Tagline</label>
                  <input
                    type="text"
                    value={formData.tagline}
                    onChange={e => setFormData(prev => ({ ...prev, tagline: e.target.value }))}
                    placeholder="es. Il vero gusto della tradizione"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Descrizione dell&apos;attivit&agrave; <span className="text-red-400">*</span></label>
                  <textarea
                    value={formData.description}
                    onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Descrivi cosa fai, i tuoi servizi, la tua storia..."
                    rows={4}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                  />
                  <p className="text-xs text-slate-500 mt-2">Suggerimento: Pi&ugrave; dettagli fornisci, migliore sar&agrave; il risultato</p>
                </div>

                {/* Logo Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2">Logo (opzionale)</label>
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
                        <p className="text-sm text-slate-400">Clicca per caricare il logo</p>
                        <p className="text-xs text-slate-600">PNG, JPG o SVG (max 2MB)</p>
                      </>
                    )}
                  </div>
                  <input ref={logoInputRef} type="file" accept="image/*" onChange={handleLogoUpload} className="hidden" />
                </div>

                {/* Contact Info */}
                <div className="pt-4 border-t border-white/10">
                  <label className="block text-sm font-medium mb-4">Informazioni di contatto</label>
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
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ===== STEP 3: Foto ===== */}
          {currentStep === 3 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Carica le tue foto</h1>
                <p className="text-slate-400">Aggiungi foto della tua attivit&agrave; per riempire il sito (opzionale, max 8)</p>
              </div>

              <div className="max-w-3xl mx-auto">
                {/* Photo Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
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

                  {/* Add Photo Button */}
                  {formData.photos.length < 8 && (
                    <button
                      onClick={() => photoInputRef.current?.click()}
                      className="aspect-square rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all flex flex-col items-center justify-center gap-2"
                    >
                      <PlusIcon className="w-8 h-8 text-slate-500" />
                      <span className="text-xs text-slate-400">Aggiungi foto</span>
                    </button>
                  )}
                </div>

                <input ref={photoInputRef} type="file" accept="image/*" multiple onChange={handlePhotoUpload} className="hidden" />

                <p className="text-center text-sm text-slate-500 mt-6">
                  Le foto verranno usate dall&apos;AI per riempire le sezioni del sito.
                  Se non carichi foto, l&apos;AI user&agrave; immagini professionali di stock.
                </p>
              </div>
            </div>
          )}

          {/* ===== STEP 4: Review & Genera ===== */}
          {currentStep === 4 && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="text-center mb-12">
                <h1 className="text-3xl font-bold mb-3">Review & Genera</h1>
                <p className="text-slate-400">Controlla le informazioni prima di generare il sito</p>
              </div>

              <div className="max-w-2xl mx-auto space-y-6">
                {/* Template Summary */}
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                  <h3 className="font-medium mb-4 flex items-center gap-2">
                    <PaintBrushIcon className="w-5 h-5 text-violet-400" />
                    Template & Stile
                  </h3>
                  <div className="flex items-center gap-4">
                    {selectedStyle && (
                      <>
                        <div className="w-16 h-16 rounded-xl overflow-hidden relative flex-shrink-0">
                          <Image src={selectedStyle.image} alt={selectedStyle.label} fill className="object-cover" />
                        </div>
                        <div>
                          <p className="font-medium">{selectedCategory?.label} &mdash; {selectedStyle.label}</p>
                          <p className="text-sm text-slate-400">{selectedStyle.description}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: selectedStyle.primaryColor }} />
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: selectedStyle.secondaryColor }} />
                            <span className="text-xs text-slate-500">{selectedStyle.sections.length} sezioni</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Brand Summary */}
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
                    {formData.logo && (
                      <div className="flex justify-between items-center">
                        <span className="text-slate-500">Logo</span>
                        <div className="w-8 h-8 rounded overflow-hidden relative"><Image src={formData.logo} alt="Logo" fill className="object-contain" /></div>
                      </div>
                    )}
                  </dl>
                </div>

                {/* Photos Summary */}
                {formData.photos.length > 0 && (
                  <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                    <h3 className="font-medium mb-4 flex items-center gap-2">
                      <PhotoIcon className="w-5 h-5 text-emerald-400" />
                      Foto ({formData.photos.length})
                    </h3>
                    <div className="flex gap-2 overflow-x-auto">
                      {formData.photos.map(photo => (
                        <div key={photo.id} className="w-16 h-16 rounded-lg overflow-hidden relative flex-shrink-0">
                          <Image src={photo.dataUrl} alt="" fill className="object-cover" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sections */}
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
                  <h3 className="font-medium mb-4 flex items-center gap-2">
                    <DocumentTextIcon className="w-5 h-5 text-emerald-400" />
                    Sezioni ({selectedStyle?.sections.length || 0})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedStyle?.sections.map(s => (
                      <span key={s} className="px-3 py-1 rounded-full bg-white/5 text-sm text-slate-300">
                        {SECTION_LABELS[s] || s}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Generate */}
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
                      className="w-full py-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl font-semibold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-3"
                    >
                      <SparklesIcon className="w-5 h-5" />
                      Genera il Mio Sito
                    </button>
                    <p className="text-center text-sm text-slate-500">
                      Pipeline AI a 4 step &mdash; Tempo stimato: 40-60 secondi
                    </p>
                  </>
                )}
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
            Indietro
          </button>

          <div className="md:hidden text-sm text-slate-400">
            Passo {currentStep + 1} di {WIZARD_STEPS.length}
          </div>

          <button
            onClick={() => {
              if (currentStep === 4) {
                handleGenerate();
              } else {
                setCurrentStep(prev => Math.min(4, prev + 1));
              }
            }}
            disabled={!canProceed() || isGenerating}
            className="flex items-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-full font-medium transition-all"
          >
            {currentStep === 4 ? "Genera" : "Avanti"}
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
                    <Dialog.Title as="h3" className="text-xl font-semibold mb-2">Hai esaurito le generazioni gratuite</Dialog.Title>
                    <p className="text-slate-400 mb-6">Passa a un piano a pagamento per pi&ugrave; generazioni.</p>
                    <div className="flex gap-3">
                      <button onClick={() => setShowUpgradeModal(false)} className="flex-1 px-4 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                        Pi&ugrave; tardi
                      </button>
                      <button onClick={handleUpgrade} disabled={isUpgrading} className="flex-1 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 rounded-lg font-medium transition-all disabled:opacity-50">
                        {isUpgrading ? "Attivazione..." : "Upgrade (DEMO)"}
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
