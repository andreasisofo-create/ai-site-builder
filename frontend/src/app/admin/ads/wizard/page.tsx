"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Target,
  DollarSign,
  Users,
  Image,
  FileText,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Sparkles,
  Wand2,
  Wrench,
  Globe,
  MessageCircle,
  ShoppingCart,
  Eye,
  UserPlus,
  MapPin,
  Plus,
  Minus,
  AlertTriangle,
  Check,
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
// Types
// ---------------------------------------------------------------------------
type WizardMode = "guided" | "assisted" | "manual";

interface WizardStep {
  id: string;
  name: string;
  icon: typeof Target;
}

interface Objective {
  id: string;
  name: string;
  metaObjective: string;
  bestFor: string[];
}

interface BudgetTemplate {
  id: string;
  name: string;
  daily: number | null;
  monthly: number | null;
  duration: number | null;
}

interface Client {
  id: number;
  businessName: string;
  businessType: string;
  city?: string;
  websiteUrl?: string;
}

interface AudienceData {
  ageMin: number;
  ageMax: number;
  radius: number;
  interests: string[];
  gender: "all" | "male" | "female";
}

interface AdCopyVariation {
  headline: string;
  primaryText: string;
  cta: string;
}

// ---------------------------------------------------------------------------
// Static data
// ---------------------------------------------------------------------------
const STEPS: WizardStep[] = [
  { id: "objective", name: "Obiettivo", icon: Target },
  { id: "budget", name: "Budget", icon: DollarSign },
  { id: "audience", name: "Pubblico", icon: Users },
  { id: "content", name: "Contenuto", icon: Image },
  { id: "ad_copy", name: "Testo Annuncio", icon: FileText },
  { id: "review", name: "Riepilogo", icon: CheckCircle },
];

const OBJECTIVES: Objective[] = [
  {
    id: "awareness",
    name: "Piu Follower",
    metaObjective: "AWARENESS",
    bestFor: ["ristorazione", "fitness", "estetica", "retail"],
  },
  {
    id: "traffic",
    name: "Piu Visite al Sito",
    metaObjective: "TRAFFIC",
    bestFor: ["ecommerce", "servizi", "tech"],
  },
  {
    id: "leads",
    name: "Piu Contatti",
    metaObjective: "LEADS",
    bestFor: ["servizi_legali", "sanita", "immobiliare", "servizi_professionali"],
  },
  {
    id: "messages",
    name: "Piu Messaggi",
    metaObjective: "MESSAGES",
    bestFor: ["ristorazione", "estetica", "fitness", "edile"],
  },
  {
    id: "conversions",
    name: "Piu Vendite",
    metaObjective: "SALES",
    bestFor: ["ecommerce", "retail"],
  },
];

const OBJECTIVE_ICONS: Record<string, typeof Target> = {
  awareness: Eye,
  traffic: Globe,
  leads: UserPlus,
  messages: MessageCircle,
  conversions: ShoppingCart,
};

const OBJECTIVE_DESCRIPTIONS: Record<string, string> = {
  awareness:
    "La campagna mostrera i tuoi contenuti a persone che potrebbero essere interessate ma non ti seguono ancora.",
  traffic:
    "Meta trovera persone che tendono a cliccare sui link e visitare siti web.",
  leads:
    "Perfetto per servizi B2B o consulenze. Le persone lasciano i loro dati in un modulo.",
  messages:
    "Ideale per prenotazioni, preventivi, domande immediate. Il cliente ti contatta direttamente.",
  conversions:
    "Richiede Meta Pixel installato. Ottimizza per acquisti reali.",
};

const BUDGET_TEMPLATES: BudgetTemplate[] = [
  { id: "starter", name: "Starter", daily: 5, monthly: 150, duration: 30 },
  { id: "standard", name: "Standard", daily: 10, monthly: 300, duration: 30 },
  { id: "pro", name: "Pro", daily: 20, monthly: 600, duration: 30 },
  { id: "custom", name: "Personalizzato", daily: null, monthly: null, duration: null },
];

const BUDGET_DESCRIPTIONS: Record<string, string> = {
  starter: "Per iniziare e testare - 500-1.500 persone/mese",
  standard: "Il piu scelto dai clienti - 1.500-4.000 persone/mese",
  pro: "Per risultati consistenti - 4.000-10.000 persone/mese",
  custom: "Decidi tu importo e durata",
};

const DEFAULT_INTERESTS: Record<string, string[]> = {
  ristorazione: ["Cibo", "Ristoranti", "Cucina italiana", "Uscire"],
  fitness: ["Fitness", "Palestra", "Allenamento", "Benessere"],
  estetica: ["Bellezza", "Cura personale", "Moda", "Lifestyle"],
  servizi_legali: ["Business", "Imprenditoria", "Gestione aziendale"],
  ecommerce: ["Shopping online", "E-commerce", "Moda"],
  immobiliare: ["Immobiliare", "Casa", "Investimenti"],
  default: ["Lifestyle", "Shopping", "Servizi locali"],
};

const AD_COPY_TEMPLATES: Record<string, AdCopyVariation[]> = {
  messages: [
    {
      headline: "Scrivici ora!",
      primaryText:
        "Hai domande? Siamo qui per aiutarti! Scrivici per info, prenotazioni o preventivi. Ti rispondiamo in pochi minuti!",
      cta: "Messaggio",
    },
    {
      headline: "Info e prenotazioni",
      primaryText:
        "Scopri come possiamo esserti utili. Mandaci un messaggio e ricevi una risposta immediata.",
      cta: "Messaggio",
    },
  ],
  leads: [
    {
      headline: "Richiedi info gratuita",
      primaryText:
        "Lascia i tuoi dati e ti contattiamo entro 24h con un preventivo personalizzato.",
      cta: "Scopri di piu",
    },
  ],
  awareness: [
    {
      headline: "Scopri chi siamo",
      primaryText:
        "Seguici per scoprire le novita e le offerte speciali!",
      cta: "Segui",
    },
  ],
  traffic: [
    {
      headline: "Visita il nostro sito",
      primaryText:
        "Scopri tutti i nostri servizi e prodotti sul sito web. Offerte esclusive ti aspettano!",
      cta: "Scopri di piu",
    },
  ],
  conversions: [
    {
      headline: "Acquista ora",
      primaryText:
        "Prodotti selezionati per te. Spedizione veloce, reso gratuito. Scopri le offerte!",
      cta: "Acquista ora",
    },
  ],
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function CampaignWizardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  // Wizard state
  const [mode, setMode] = useState<WizardMode | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardId, setWizardId] = useState<number | null>(null);

  // Client selection
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  // Step data
  const [selectedObjective, setSelectedObjective] = useState<string | null>(null);
  const [selectedBudget, setSelectedBudget] = useState<string>("standard");
  const [customBudget, setCustomBudget] = useState({ daily: 10, duration: 30 });
  const [audience, setAudience] = useState<AudienceData>({
    ageMin: 25,
    ageMax: 55,
    radius: 15,
    interests: [],
    gender: "all",
  });
  const [contentType, setContentType] = useState<string>("reel");
  const [selectedAdCopy, setSelectedAdCopy] = useState<number>(0);
  const [customAdCopy, setCustomAdCopy] = useState<AdCopyVariation>({
    headline: "",
    primaryText: "",
    cta: "Messaggio",
  });
  const [useCustomCopy, setUseCustomCopy] = useState(false);

  // Submitting state
  const [submitting, setSubmitting] = useState(false);

  // Load clients on mount
  useEffect(() => {
    const load = async () => {
      try {
        const data = await adminFetch("/api/ads/clients");
        const list = data.data || data.clients || [];
        setClients(
          list.map((c: any) => ({
            id: c.id,
            businessName: c.business_name || c.businessName || c.name,
            businessType: c.business_type || c.businessType || "",
            city: c.city,
            websiteUrl: c.website_url || c.websiteUrl || c.website,
          }))
        );
      } catch {
        // API not available yet
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Set default interests when client is selected
  useEffect(() => {
    if (selectedClient) {
      const key = selectedClient.businessType;
      setAudience((prev) => ({
        ...prev,
        interests: DEFAULT_INTERESTS[key] || DEFAULT_INTERESTS.default,
      }));
    }
  }, [selectedClient]);

  // Start wizard on backend
  const startWizard = useCallback(
    async (wizardMode: WizardMode) => {
      if (!selectedClient) return;
      setMode(wizardMode);
      try {
        const res = await adminFetch("/api/ads/wizard/start", {
          method: "POST",
          body: JSON.stringify({
            client_id: selectedClient.id,
            mode: wizardMode,
          }),
        });
        if (res.success && res.data?.wizardId) {
          setWizardId(res.data.wizardId);
        }
      } catch {
        // Continue without backend tracking
      }
      setCurrentStep(0);
    },
    [selectedClient]
  );

  // Save step to backend
  const saveStep = useCallback(
    async (stepId: string, data: any) => {
      if (!wizardId) return;
      try {
        await adminFetch(`/api/ads/wizard/step/${stepId}`, {
          method: "POST",
          body: JSON.stringify({ wizard_id: wizardId, data }),
        });
      } catch {
        // Silent
      }
    },
    [wizardId]
  );

  // Complete wizard
  const completeWizard = useCallback(async () => {
    setSubmitting(true);
    const budgetTpl = BUDGET_TEMPLATES.find((b) => b.id === selectedBudget);
    const dailyBudget =
      selectedBudget === "custom" ? customBudget.daily : budgetTpl?.daily || 10;
    const duration =
      selectedBudget === "custom" ? customBudget.duration : budgetTpl?.duration || 30;
    const adCopyData = useCustomCopy
      ? customAdCopy
      : (AD_COPY_TEMPLATES[selectedObjective || "messages"] || AD_COPY_TEMPLATES.messages)[
          selectedAdCopy
        ];

    const campaignData = {
      mode,
      objective: selectedObjective,
      budget: { daily: dailyBudget, monthly: dailyBudget * duration, duration },
      audience,
      contentType,
      adCopy: adCopyData,
      clientId: selectedClient?.id,
      platform: "meta",
    };

    try {
      if (wizardId) {
        await adminFetch("/api/ads/wizard/complete", {
          method: "POST",
          body: JSON.stringify({
            wizard_id: wizardId,
            campaign_data: campaignData,
          }),
        });
      }
      // Navigate back to campaigns
      router.push("/admin/ads/campaigns");
    } catch {
      // Silent
    } finally {
      setSubmitting(false);
    }
  }, [
    mode,
    selectedObjective,
    selectedBudget,
    customBudget,
    audience,
    contentType,
    selectedAdCopy,
    customAdCopy,
    useCustomCopy,
    selectedClient,
    wizardId,
    router,
  ]);

  const canAdvance = (): boolean => {
    const stepId = STEPS[currentStep]?.id;
    switch (stepId) {
      case "objective":
        return !!selectedObjective;
      case "budget":
        return selectedBudget === "custom" ? customBudget.daily >= 3 : true;
      case "audience":
        return audience.ageMin < audience.ageMax && audience.radius > 0;
      case "content":
        return !!contentType;
      case "ad_copy": {
        if (useCustomCopy) {
          return customAdCopy.headline.length > 0 && customAdCopy.primaryText.length > 10;
        }
        return true;
      }
      case "review":
        return true;
      default:
        return true;
    }
  };

  const handleNext = async () => {
    const stepId = STEPS[currentStep]?.id;
    // Save current step data
    const stepDataMap: Record<string, any> = {
      objective: { objective: selectedObjective },
      budget: {
        template: selectedBudget,
        daily: selectedBudget === "custom" ? customBudget.daily : BUDGET_TEMPLATES.find((b) => b.id === selectedBudget)?.daily,
        duration: selectedBudget === "custom" ? customBudget.duration : 30,
      },
      audience,
      content: { type: contentType },
      ad_copy: useCustomCopy
        ? customAdCopy
        : (AD_COPY_TEMPLATES[selectedObjective || "messages"] || AD_COPY_TEMPLATES.messages)[selectedAdCopy],
    };

    if (stepId && stepDataMap[stepId]) {
      saveStep(stepId, stepDataMap[stepId]);
    }

    if (currentStep < STEPS.length - 1) {
      setCurrentStep((s) => s + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
    }
  };

  // =========================================================================
  // Render - Mode Selection
  // =========================================================================
  if (!selectedClient) {
    return (
      <div className="space-y-8 max-w-4xl mx-auto">
        <div>
          <button
            onClick={() => router.push("/admin/ads/campaigns")}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm mb-6"
          >
            <ChevronLeft className="w-4 h-4" />
            Torna alle Campagne
          </button>
          <h1 className="text-2xl font-bold text-white">Creazione Campagna</h1>
          <p className="text-gray-500 mt-1">Seleziona il cliente per cui creare la campagna</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 className="w-8 h-8 text-amber-400 animate-spin" />
          </div>
        ) : clients.length === 0 ? (
          <div className="rounded-xl border-2 border-dashed border-white/10 p-12 text-center">
            <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-amber-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Nessun cliente</h3>
            <p className="text-gray-400 max-w-md mx-auto mb-6">
              Aggiungi un cliente prima di creare una campagna.
            </p>
            <button
              onClick={() => router.push("/admin/ads/clients")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Vai ai Clienti
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {clients.map((client) => (
              <button
                key={client.id}
                onClick={() => setSelectedClient(client)}
                className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-amber-500/30 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-500/10 flex items-center justify-center text-2xl font-bold text-amber-300 shrink-0">
                    {(client.businessName || "C").charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white group-hover:text-amber-400 transition-colors">
                      {client.businessName}
                    </h3>
                    <p className="text-sm text-gray-500 capitalize">{client.businessType}</p>
                    {client.city && (
                      <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
                        <MapPin className="w-3 h-3" />
                        {client.city}
                      </div>
                    )}
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-amber-400 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (mode === null) {
    return (
      <div className="space-y-8 max-w-4xl mx-auto">
        <div>
          <button
            onClick={() => setSelectedClient(null)}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm mb-6"
          >
            <ChevronLeft className="w-4 h-4" />
            Cambia Cliente
          </button>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center text-lg font-bold text-amber-300">
              {selectedClient.businessName.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Scegli la Modalita</h1>
              <p className="text-gray-500">
                Campagna per <span className="text-amber-400">{selectedClient.businessName}</span>
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Guided */}
          <button
            onClick={() => startWizard("guided")}
            className="rounded-xl bg-[#141420] border border-white/5 p-8 text-left hover:border-amber-500/30 transition-all group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 px-3 py-1 bg-amber-500/20 text-amber-400 text-xs font-medium rounded-bl-lg">
              Consigliato
            </div>
            <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center mb-5">
              <Sparkles className="w-7 h-7 text-amber-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-amber-400 transition-colors">
              Guidata
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Perfetto per principianti. L&apos;AI ti guida passo-passo con spiegazioni e
              suggerimenti per ogni scelta.
            </p>
            <ul className="space-y-2">
              {["Spiegazioni dettagliate", "Suggerimenti AI", "Best practice integrate"].map(
                (item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-gray-400">
                    <CheckCircle className="w-4 h-4 text-amber-400/60" />
                    {item}
                  </li>
                )
              )}
            </ul>
          </button>

          {/* Assisted */}
          <button
            onClick={() => startWizard("assisted")}
            className="rounded-xl bg-[#141420] border border-white/5 p-8 text-left hover:border-amber-500/30 transition-all group"
          >
            <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center mb-5">
              <Wand2 className="w-7 h-7 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-amber-400 transition-colors">
              Assistita
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Per utenti intermedi. Suggerimenti disponibili ma piena liberta di
              personalizzazione.
            </p>
            <ul className="space-y-2">
              {["Suggerimenti opzionali", "Personalizzazione libera", "Controllo avanzato"].map(
                (item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-gray-400">
                    <CheckCircle className="w-4 h-4 text-blue-400/60" />
                    {item}
                  </li>
                )
              )}
            </ul>
          </button>

          {/* Manual */}
          <button
            onClick={() => startWizard("manual")}
            className="rounded-xl bg-[#141420] border border-white/5 p-8 text-left hover:border-amber-500/30 transition-all group"
          >
            <div className="w-14 h-14 rounded-xl bg-gray-500/10 flex items-center justify-center mb-5">
              <Wrench className="w-7 h-7 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-amber-400 transition-colors">
              Manuale
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Per esperti. Solo gli strumenti essenziali, nessuna guida. Massima
              velocita.
            </p>
            <ul className="space-y-2">
              {["Nessuna guida", "Configurazione diretta", "Per professionisti"].map(
                (item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-gray-400">
                    <CheckCircle className="w-4 h-4 text-gray-500/60" />
                    {item}
                  </li>
                )
              )}
            </ul>
          </button>
        </div>
      </div>
    );
  }

  // =========================================================================
  // Render - Wizard Steps
  // =========================================================================
  const stepId = STEPS[currentStep].id;
  const adCopyOptions =
    AD_COPY_TEMPLATES[selectedObjective || "messages"] || AD_COPY_TEMPLATES.messages;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => {
              if (currentStep === 0) {
                setMode(null);
              } else {
                handleBack();
              }
            }}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm mb-3"
          >
            <ChevronLeft className="w-4 h-4" />
            {currentStep === 0 ? "Cambia Modalita" : "Step Precedente"}
          </button>
          <h1 className="text-2xl font-bold text-white">
            {STEPS[currentStep].name}
          </h1>
          <p className="text-gray-500 text-sm">
            {selectedClient.businessName} &middot;{" "}
            <span className="capitalize">{mode}</span> &middot; Step{" "}
            {currentStep + 1} di {STEPS.length}
          </p>
        </div>
        <div className="text-right">
          <span
            className={`text-xs px-3 py-1 rounded-full ${
              mode === "guided"
                ? "bg-amber-500/10 text-amber-400"
                : mode === "assisted"
                ? "bg-blue-500/10 text-blue-400"
                : "bg-white/5 text-gray-400"
            }`}
          >
            {mode === "guided" ? "Guidata" : mode === "assisted" ? "Assistita" : "Manuale"}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="flex items-center gap-1">
        {STEPS.map((step, idx) => {
          const StepIcon = step.icon;
          const isActive = idx === currentStep;
          const isCompleted = idx < currentStep;
          return (
            <div key={step.id} className="flex-1 flex items-center gap-1">
              <div
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all flex-1 ${
                  isActive
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    : isCompleted
                    ? "bg-emerald-500/5 text-emerald-400"
                    : "bg-white/5 text-gray-600"
                }`}
              >
                {isCompleted ? (
                  <Check className="w-3.5 h-3.5" />
                ) : (
                  <StepIcon className="w-3.5 h-3.5" />
                )}
                <span className="hidden lg:inline">{step.name}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <div className="rounded-xl bg-[#141420] border border-white/5 p-8">
        {/* ---- STEP 1: Objective ---- */}
        {stepId === "objective" && (
          <div className="space-y-6">
            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <p className="text-sm text-gray-300">
                  Scegli l&apos;obiettivo principale della campagna. Questo determina come
                  l&apos;algoritmo ottimizzera la distribuzione degli annunci.
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {OBJECTIVES.map((obj) => {
                const ObjIcon = OBJECTIVE_ICONS[obj.id] || Target;
                const isSelected = selectedObjective === obj.id;
                const isRecommended = selectedClient?.businessType
                  ? obj.bestFor.includes(selectedClient.businessType)
                  : false;

                return (
                  <button
                    key={obj.id}
                    onClick={() => setSelectedObjective(obj.id)}
                    className={`rounded-xl border p-5 text-left transition-all relative ${
                      isSelected
                        ? "border-amber-500 ring-2 ring-amber-500/20 bg-amber-500/5"
                        : "border-white/5 hover:border-white/10 bg-[#1a1a2e]"
                    }`}
                  >
                    {isRecommended && mode !== "manual" && (
                      <span className="absolute top-3 right-3 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">
                        Consigliato
                      </span>
                    )}
                    <div className="flex items-center gap-3 mb-3">
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          isSelected ? "bg-amber-500/20" : "bg-white/5"
                        }`}
                      >
                        <ObjIcon
                          className={`w-5 h-5 ${
                            isSelected ? "text-amber-400" : "text-gray-400"
                          }`}
                        />
                      </div>
                      <h3
                        className={`font-semibold ${
                          isSelected ? "text-amber-400" : "text-white"
                        }`}
                      >
                        {obj.name}
                      </h3>
                    </div>
                    {mode !== "manual" && (
                      <p className="text-sm text-gray-500">
                        {OBJECTIVE_DESCRIPTIONS[obj.id]}
                      </p>
                    )}
                  </button>
                );
              })}
            </div>

            {mode === "guided" && selectedObjective && (
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-sm text-gray-300">
                  <span className="text-amber-400 font-medium">Consiglio: </span>
                  Scegli sempre l&apos;obiettivo piu vicino alla tua meta finale. Se vuoi
                  prenotazioni, scegli &quot;Messaggi&quot; non &quot;Follower&quot;.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ---- STEP 2: Budget ---- */}
        {stepId === "budget" && (
          <div className="space-y-6">
            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <p className="text-sm text-gray-300">
                  Il budget giornaliero determina quante persone vedranno i tuoi annunci.
                  Un budget piu alto = piu visibilita e risultati piu rapidi.
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {BUDGET_TEMPLATES.map((tpl) => {
                const isSelected = selectedBudget === tpl.id;
                return (
                  <button
                    key={tpl.id}
                    onClick={() => setSelectedBudget(tpl.id)}
                    className={`rounded-xl border p-5 text-left transition-all ${
                      isSelected
                        ? "border-amber-500 ring-2 ring-amber-500/20 bg-amber-500/5"
                        : "border-white/5 hover:border-white/10 bg-[#1a1a2e]"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3
                        className={`font-semibold ${
                          isSelected ? "text-amber-400" : "text-white"
                        }`}
                      >
                        {tpl.name}
                      </h3>
                      {tpl.daily !== null && (
                        <span className="text-lg font-bold text-white">
                          {tpl.daily}&euro;/giorno
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">
                      {BUDGET_DESCRIPTIONS[tpl.id]}
                    </p>
                    {tpl.monthly !== null && (
                      <p className="text-xs text-gray-600 mt-2">
                        Totale: &euro;{tpl.monthly} per {tpl.duration} giorni
                      </p>
                    )}
                    {tpl.id === "standard" && mode !== "manual" && (
                      <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">
                        Piu scelto
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {selectedBudget === "custom" && (
              <div className="p-5 rounded-xl bg-[#1a1a2e] border border-white/5 space-y-4">
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">
                    Budget Giornaliero (&euro;)
                  </label>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() =>
                        setCustomBudget((prev) => ({
                          ...prev,
                          daily: Math.max(3, prev.daily - 1),
                        }))
                      }
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <input
                      type="number"
                      value={customBudget.daily}
                      onChange={(e) =>
                        setCustomBudget((prev) => ({
                          ...prev,
                          daily: Math.max(3, parseInt(e.target.value) || 3),
                        }))
                      }
                      min={3}
                      className="w-24 text-center py-2 rounded-lg bg-[#141420] border border-white/10 text-white text-lg font-semibold focus:border-amber-500/50 focus:outline-none"
                    />
                    <button
                      onClick={() =>
                        setCustomBudget((prev) => ({
                          ...prev,
                          daily: prev.daily + 1,
                        }))
                      }
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                    <span className="text-gray-500">&euro;/giorno</span>
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">
                    Durata (giorni)
                  </label>
                  <input
                    type="number"
                    value={customBudget.duration}
                    onChange={(e) =>
                      setCustomBudget((prev) => ({
                        ...prev,
                        duration: Math.max(7, parseInt(e.target.value) || 7),
                      }))
                    }
                    min={7}
                    className="w-24 text-center py-2 rounded-lg bg-[#141420] border border-white/10 text-white focus:border-amber-500/50 focus:outline-none"
                  />
                </div>
                <p className="text-sm text-gray-500">
                  Totale: <strong className="text-white">&euro;{customBudget.daily * customBudget.duration}</strong>{" "}
                  per {customBudget.duration} giorni
                </p>
                {customBudget.daily < 5 && (
                  <div className="flex items-center gap-2 text-xs text-amber-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Budget sotto 5&euro;/giorno puo dare risultati limitati.
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ---- STEP 3: Audience ---- */}
        {stepId === "audience" && (
          <div className="space-y-6">
            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <p className="text-sm text-gray-300">
                  Definisci chi vedra i tuoi annunci. Non restringere troppo -
                  lascia che l&apos;algoritmo trovi le persone giuste.
                </p>
              </div>
            )}

            {/* Age Range */}
            <div className="p-5 rounded-xl bg-[#1a1a2e] border border-white/5">
              <h4 className="font-medium text-white mb-4">Fascia di Eta</h4>
              <div className="flex items-center gap-4">
                <div>
                  <label className="text-xs text-gray-500 block mb-1">Da</label>
                  <input
                    type="number"
                    value={audience.ageMin}
                    onChange={(e) =>
                      setAudience((prev) => ({
                        ...prev,
                        ageMin: Math.max(18, parseInt(e.target.value) || 18),
                      }))
                    }
                    min={18}
                    max={65}
                    className="w-20 text-center py-2 rounded-lg bg-[#141420] border border-white/10 text-white focus:border-amber-500/50 focus:outline-none text-sm"
                  />
                </div>
                <span className="text-gray-600 mt-5">-</span>
                <div>
                  <label className="text-xs text-gray-500 block mb-1">A</label>
                  <input
                    type="number"
                    value={audience.ageMax}
                    onChange={(e) =>
                      setAudience((prev) => ({
                        ...prev,
                        ageMax: Math.min(65, parseInt(e.target.value) || 65),
                      }))
                    }
                    min={18}
                    max={65}
                    className="w-20 text-center py-2 rounded-lg bg-[#141420] border border-white/10 text-white focus:border-amber-500/50 focus:outline-none text-sm"
                  />
                </div>
                <span className="text-sm text-gray-500 mt-5">anni</span>
              </div>
            </div>

            {/* Location Radius */}
            <div className="p-5 rounded-xl bg-[#1a1a2e] border border-white/5">
              <h4 className="font-medium text-white mb-4">
                <MapPin className="w-4 h-4 inline mr-1" />
                Raggio Geografico
                {selectedClient?.city && (
                  <span className="text-gray-500 font-normal"> da {selectedClient.city}</span>
                )}
              </h4>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  value={audience.radius}
                  onChange={(e) =>
                    setAudience((prev) => ({ ...prev, radius: parseInt(e.target.value) }))
                  }
                  min={1}
                  max={80}
                  className="flex-1 accent-amber-500"
                />
                <span className="text-white font-semibold w-16 text-right">
                  {audience.radius} km
                </span>
              </div>
            </div>

            {/* Gender */}
            <div className="p-5 rounded-xl bg-[#1a1a2e] border border-white/5">
              <h4 className="font-medium text-white mb-4">Genere</h4>
              <div className="flex gap-3">
                {(["all", "male", "female"] as const).map((g) => {
                  const labels = { all: "Tutti", male: "Uomini", female: "Donne" };
                  return (
                    <button
                      key={g}
                      onClick={() => setAudience((prev) => ({ ...prev, gender: g }))}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                        audience.gender === g
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-white/5 text-gray-400 hover:bg-white/10"
                      }`}
                    >
                      {labels[g]}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Interests */}
            <div className="p-5 rounded-xl bg-[#1a1a2e] border border-white/5">
              <h4 className="font-medium text-white mb-4">Interessi</h4>
              <div className="flex flex-wrap gap-2">
                {audience.interests.map((interest, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-400 text-sm"
                  >
                    {interest}
                    <button
                      onClick={() =>
                        setAudience((prev) => ({
                          ...prev,
                          interests: prev.interests.filter((_, i) => i !== idx),
                        }))
                      }
                      className="hover:text-white"
                    >
                      &times;
                    </button>
                  </span>
                ))}
                <button
                  onClick={() => {
                    const input = prompt("Aggiungi interesse:");
                    if (input?.trim()) {
                      setAudience((prev) => ({
                        ...prev,
                        interests: [...prev.interests, input.trim()],
                      }));
                    }
                  }}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-white/5 text-gray-400 text-sm hover:bg-white/10 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Aggiungi
                </button>
              </div>
            </div>

            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-sm text-gray-300">
                  <span className="text-amber-400 font-medium">Consiglio: </span>
                  Non restringere troppo il pubblico! Lascia fare all&apos;algoritmo di Meta,
                  che ottimizzera automaticamente la distribuzione.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ---- STEP 4: Content ---- */}
        {stepId === "content" && (
          <div className="space-y-6">
            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <p className="text-sm text-gray-300">
                  Scegli il tipo di contenuto per il tuo annuncio. I Reel hanno le migliori
                  performance nel 2026!
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                {
                  id: "reel",
                  name: "Reel / Video Breve",
                  desc: "15-30 secondi con movimento. Le migliori performance!",
                  badge: "Consigliato",
                },
                {
                  id: "carousel",
                  name: "Carousel",
                  desc: "Foto multiple per mostrare servizi o prodotti.",
                  badge: null,
                },
                {
                  id: "image",
                  name: "Immagine Singola",
                  desc: "Una foto impattante per catturare l'attenzione.",
                  badge: null,
                },
                {
                  id: "story",
                  name: "Story",
                  desc: "Formato verticale per offerte e dietro le quinte.",
                  badge: null,
                },
              ].map((ct) => {
                const isSelected = contentType === ct.id;
                return (
                  <button
                    key={ct.id}
                    onClick={() => setContentType(ct.id)}
                    className={`rounded-xl border p-5 text-left transition-all relative ${
                      isSelected
                        ? "border-amber-500 ring-2 ring-amber-500/20 bg-amber-500/5"
                        : "border-white/5 hover:border-white/10 bg-[#1a1a2e]"
                    }`}
                  >
                    {ct.badge && mode !== "manual" && (
                      <span className="absolute top-3 right-3 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">
                        {ct.badge}
                      </span>
                    )}
                    <h3
                      className={`font-semibold mb-1 ${
                        isSelected ? "text-amber-400" : "text-white"
                      }`}
                    >
                      {ct.name}
                    </h3>
                    {mode !== "manual" && (
                      <p className="text-sm text-gray-500">{ct.desc}</p>
                    )}
                  </button>
                );
              })}
            </div>

            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-sm text-gray-300">
                  <span className="text-amber-400 font-medium">Regola d&apos;oro: </span>
                  Mai promuovere un post che ha avuto meno di 10 interazioni organiche.
                  Promuovi contenuti che funzionano gia!
                </p>
              </div>
            )}
          </div>
        )}

        {/* ---- STEP 5: Ad Copy ---- */}
        {stepId === "ad_copy" && (
          <div className="space-y-6">
            {mode === "guided" && (
              <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <div className="space-y-2 text-sm text-gray-300">
                  <p>
                    <span className="text-amber-400 font-medium">Hook: </span>
                    La prima frase deve fermare lo scrolling. Parla del beneficio per il
                    cliente.
                  </p>
                  <p>
                    <span className="text-amber-400 font-medium">Body: </span>
                    Spiega chiaramente cosa offri e perche sei diverso.
                  </p>
                  <p>
                    <span className="text-amber-400 font-medium">CTA: </span>
                    Il Call to Action deve essere chiaro e urgente.
                  </p>
                  <p className="text-xs text-gray-500">
                    Testo max 125 caratteri per la prima riga (prima di
                    &quot;...altro&quot;)
                  </p>
                </div>
              </div>
            )}

            {/* Toggle custom/template */}
            <div className="flex gap-3">
              <button
                onClick={() => setUseCustomCopy(false)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  !useCustomCopy
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    : "bg-white/5 text-gray-400 hover:bg-white/10"
                }`}
              >
                Suggerimenti AI
              </button>
              <button
                onClick={() => setUseCustomCopy(true)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  useCustomCopy
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    : "bg-white/5 text-gray-400 hover:bg-white/10"
                }`}
              >
                Scrivi Personalmente
              </button>
            </div>

            {!useCustomCopy ? (
              <div className="space-y-4">
                {adCopyOptions.map((copy, idx) => {
                  const isSelected = selectedAdCopy === idx;
                  return (
                    <button
                      key={idx}
                      onClick={() => setSelectedAdCopy(idx)}
                      className={`w-full rounded-xl border p-5 text-left transition-all ${
                        isSelected
                          ? "border-amber-500 ring-2 ring-amber-500/20 bg-amber-500/5"
                          : "border-white/5 hover:border-white/10 bg-[#1a1a2e]"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-500">
                          Variante {idx + 1}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            isSelected
                              ? "bg-amber-500/10 text-amber-400"
                              : "bg-white/5 text-gray-500"
                          }`}
                        >
                          CTA: {copy.cta}
                        </span>
                      </div>
                      <h4
                        className={`font-semibold mb-2 ${
                          isSelected ? "text-amber-400" : "text-white"
                        }`}
                      >
                        {selectedClient?.businessName
                          ? `${selectedClient.businessName} - ${copy.headline}`
                          : copy.headline}
                      </h4>
                      <p className="text-sm text-gray-400">{copy.primaryText}</p>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-4 p-5 rounded-xl bg-[#1a1a2e] border border-white/5">
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Headline</label>
                  <input
                    type="text"
                    value={customAdCopy.headline}
                    onChange={(e) =>
                      setCustomAdCopy((prev) => ({ ...prev, headline: e.target.value }))
                    }
                    placeholder="Es: Scrivici ora per info!"
                    className="w-full py-2.5 px-4 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">
                    Testo Principale
                  </label>
                  <textarea
                    value={customAdCopy.primaryText}
                    onChange={(e) =>
                      setCustomAdCopy((prev) => ({
                        ...prev,
                        primaryText: e.target.value,
                      }))
                    }
                    placeholder="Descrivi la tua offerta..."
                    rows={4}
                    className="w-full py-2.5 px-4 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm resize-none"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    {customAdCopy.primaryText.length}/125 caratteri (prima riga visibile)
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">
                    Call to Action
                  </label>
                  <select
                    value={customAdCopy.cta}
                    onChange={(e) =>
                      setCustomAdCopy((prev) => ({ ...prev, cta: e.target.value }))
                    }
                    className="w-full py-2.5 px-4 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-amber-500/50 focus:outline-none"
                  >
                    <option value="Messaggio">Messaggio</option>
                    <option value="Scopri di piu">Scopri di piu</option>
                    <option value="Acquista ora">Acquista ora</option>
                    <option value="Registrati">Registrati</option>
                    <option value="Prenota">Prenota</option>
                    <option value="Contattaci">Contattaci</option>
                    <option value="Segui">Segui</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ---- STEP 6: Review ---- */}
        {stepId === "review" && (
          <div className="space-y-6">
            <div className="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <p className="text-sm text-emerald-400 font-medium">Riepilogo Campagna</p>
              </div>
              <p className="text-sm text-gray-400">
                Controlla tutti i dettagli prima di confermare la creazione.
              </p>
            </div>

            {/* Summary cards */}
            <div className="space-y-4">
              {/* Client */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Cliente</p>
                <p className="text-white font-medium">{selectedClient?.businessName}</p>
                <p className="text-sm text-gray-500 capitalize">
                  {selectedClient?.businessType}
                  {selectedClient?.city && ` - ${selectedClient.city}`}
                </p>
              </div>

              {/* Objective */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                  Obiettivo
                </p>
                <p className="text-white font-medium">
                  {OBJECTIVES.find((o) => o.id === selectedObjective)?.name || "-"}
                </p>
              </div>

              {/* Budget */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">Budget</p>
                {(() => {
                  const tpl = BUDGET_TEMPLATES.find((b) => b.id === selectedBudget);
                  const daily =
                    selectedBudget === "custom" ? customBudget.daily : tpl?.daily || 0;
                  const dur =
                    selectedBudget === "custom"
                      ? customBudget.duration
                      : tpl?.duration || 30;
                  return (
                    <>
                      <p className="text-white font-medium">
                        &euro;{daily}/giorno &middot; {dur} giorni
                      </p>
                      <p className="text-sm text-gray-500">
                        Totale: &euro;{daily * dur}
                      </p>
                    </>
                  );
                })()}
              </div>

              {/* Audience */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                  Pubblico
                </p>
                <p className="text-white font-medium">
                  {audience.ageMin}-{audience.ageMax} anni &middot; {audience.radius}km
                  {audience.gender !== "all" &&
                    ` \u00B7 ${audience.gender === "male" ? "Uomini" : "Donne"}`}
                </p>
                {audience.interests.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {audience.interests.map((i, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400"
                      >
                        {i}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                  Contenuto
                </p>
                <p className="text-white font-medium capitalize">{contentType}</p>
              </div>

              {/* Ad Copy */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                  Testo Annuncio
                </p>
                {(() => {
                  const copy = useCustomCopy
                    ? customAdCopy
                    : adCopyOptions[selectedAdCopy];
                  return (
                    <>
                      <p className="text-white font-medium">{copy?.headline}</p>
                      <p className="text-sm text-gray-400 mt-1">
                        {copy?.primaryText}
                      </p>
                      <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400">
                        CTA: {copy?.cta}
                      </span>
                    </>
                  );
                })()}
              </div>

              {/* Platform */}
              <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
                <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                  Piattaforma
                </p>
                <p className="text-white font-medium">Meta Ads</p>
                <div className="flex gap-2 mt-2">
                  {["Feed", "Stories", "Reels"].map((p) => (
                    <span
                      key={p}
                      className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Safety checks */}
            <div className="p-4 rounded-lg bg-[#1a1a2e] border border-white/5">
              <p className="text-xs text-gray-600 uppercase tracking-wider mb-3">
                Controlli di Sicurezza
              </p>
              <div className="space-y-2">
                {(() => {
                  const tpl = BUDGET_TEMPLATES.find((b) => b.id === selectedBudget);
                  const daily =
                    selectedBudget === "custom" ? customBudget.daily : tpl?.daily || 0;
                  const copy = useCustomCopy
                    ? customAdCopy
                    : adCopyOptions[selectedAdCopy];
                  const checks = [
                    { ok: daily >= 5, msg: "Budget sufficiente" },
                    { ok: audience.radius <= 50, msg: "Targeting geografico appropriato" },
                    {
                      ok: (copy?.primaryText?.length || 0) > 20,
                      msg: "Testo annuncio adeguato",
                    },
                  ];
                  return checks.map((c, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      {c.ok ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                      )}
                      <span
                        className={`text-sm ${c.ok ? "text-gray-300" : "text-amber-400"}`}
                      >
                        {c.msg}
                      </span>
                    </div>
                  ));
                })()}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 0}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-white/10 text-white text-sm font-medium hover:bg-white/5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-4 h-4" />
          Indietro
        </button>

        {stepId === "review" ? (
          <button
            onClick={completeWizard}
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors disabled:opacity-50"
          >
            {submitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle className="w-4 h-4" />
            )}
            {submitting ? "Creazione..." : "Crea Campagna"}
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!canAdvance()}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Avanti
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
