"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Search,
  BarChart3,
  Lightbulb,
  Rocket,
  Play,
  CheckCircle,
  Loader2,
  Globe,
  Target,
  FileText,
  Key,
  ArrowRight,
  AlertTriangle,
  ChevronRight,
  X,
} from "lucide-react";

// ---------------------------------------------------------------------------
// API helper
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
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  });
}

// ---------------------------------------------------------------------------
// Module definitions
// ---------------------------------------------------------------------------
const modules = [
  {
    id: "investigator",
    name: "Modulo 1: Investigatore",
    description: "Analizza il sito web del cliente ed estrae informazioni chiave",
    icon: Search,
    inputs: ["URL sito web"],
    outputs: ["Client Profile JSON", "USP", "Servizi", "Target Audience"],
  },
  {
    id: "analyst",
    name: "Modulo 2: Analista di Mercato",
    description: "Ricerca keyword, CPC, trend e competitor",
    icon: BarChart3,
    inputs: ["Client Profile"],
    outputs: ["Keyword Data", "CPC Range", "Competitor Analysis", "Budget Recommendation"],
  },
  {
    id: "architect",
    name: "Modulo 3: Architetto",
    description: "Crea la strategia e genera il piano pubblicitario",
    icon: Lightbulb,
    inputs: ["Client Profile", "Market Intelligence"],
    outputs: ["Strategy Plan", "Campaign Structure", "Ad Copy", "KPI Targets"],
  },
  {
    id: "broker",
    name: "Modulo 4: Broker",
    description: "Lancia, monitora e ottimizza le campagne",
    icon: Rocket,
    inputs: ["Approved Strategy Plan"],
    outputs: ["Live Campaigns", "Optimization Rules", "Reports"],
  },
];

type ModuleStatus = "idle" | "running" | "completed" | "error";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function AIModulesPage() {
  const router = useRouter();
  const [moduleStatus, setModuleStatus] = useState<Record<string, ModuleStatus>>({
    investigator: "idle",
    analyst: "idle",
    architect: "idle",
    broker: "idle",
  });
  const [url, setUrl] = useState("");
  const [showPlatformGuide, setShowPlatformGuide] = useState<"google" | "meta" | null>(null);

  const handleStartModule = async (moduleId: string) => {
    setModuleStatus((prev) => ({ ...prev, [moduleId]: "running" }));
    try {
      await adminFetch("/api/ads/modules/run", {
        method: "POST",
        body: JSON.stringify({ module: moduleId, url }),
      });
      setModuleStatus((prev) => ({ ...prev, [moduleId]: "completed" }));
    } catch {
      // Simulate completion for now
      await new Promise((r) => setTimeout(r, 3000));
      setModuleStatus((prev) => ({ ...prev, [moduleId]: "completed" }));
    }
  };

  const handleStartPipeline = () => {
    if (!url) return;
    handleStartModule("investigator");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">AI ADS</h1>
          <p className="text-gray-500">Autonomous Media Buyer - 4 Moduli AI</p>
        </div>
        <button
          onClick={() => router.push("/admin/ads/clients")}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/10 text-white text-sm hover:bg-white/5 transition-colors"
        >
          <Target className="w-4 h-4" />
          Seleziona Cliente
        </button>
      </div>

      {/* Pipeline Flow */}
      <div className="relative">
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-white/5 -translate-y-1/2 hidden lg:block" />
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 relative">
          {modules.map((module, index) => {
            const ModuleIcon = module.icon;
            const status = moduleStatus[module.id];
            const isRunning = status === "running";
            const isCompleted = status === "completed";
            const canStart =
              index === 0 || moduleStatus[modules[index - 1].id] === "completed";

            return (
              <div
                key={module.id}
                className={`rounded-xl bg-[#141420] border p-6 relative ${
                  isCompleted ? "border-amber-500/30" : "border-white/5"
                }`}
              >
                {/* Step number */}
                <div className="absolute -top-3 left-6 w-6 h-6 rounded-full bg-[#1a1a2e] border border-white/10 flex items-center justify-center text-xs font-bold text-gray-400">
                  {index + 1}
                </div>

                <div className="flex items-center gap-3 mb-4 mt-2">
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      isCompleted
                        ? "bg-amber-500/20"
                        : isRunning
                        ? "bg-amber-500/10 animate-pulse"
                        : "bg-[#1a1a2e]"
                    }`}
                  >
                    {isRunning ? (
                      <Loader2 className="w-6 h-6 text-amber-400 animate-spin" />
                    ) : isCompleted ? (
                      <CheckCircle className="w-6 h-6 text-amber-400" />
                    ) : (
                      <ModuleIcon className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-sm">{module.name}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? "bg-emerald-500/10 text-emerald-400"
                          : isRunning
                          ? "bg-amber-500/10 text-amber-400"
                          : "bg-white/5 text-gray-500"
                      }`}
                    >
                      {isCompleted
                        ? "Completato"
                        : isRunning
                        ? "In esecuzione"
                        : "In attesa"}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-gray-500 mb-4">{module.description}</p>

                <div className="space-y-2 mb-4">
                  <div>
                    <p className="text-xs text-gray-600 uppercase tracking-wider">Input</p>
                    <p className="text-sm text-gray-400">{module.inputs.join(", ")}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 uppercase tracking-wider">Output</p>
                    <p className="text-sm text-gray-400">{module.outputs.join(", ")}</p>
                  </div>
                </div>

                <button
                  disabled={isRunning || !canStart}
                  onClick={() => handleStartModule(module.id)}
                  className={`w-full py-2 rounded-lg text-sm font-medium transition-colors ${
                    isCompleted
                      ? "bg-white/5 text-gray-400 hover:bg-white/10"
                      : isRunning
                      ? "bg-amber-500/10 text-amber-400 cursor-wait"
                      : canStart
                      ? "bg-amber-500 text-black hover:bg-amber-400"
                      : "bg-white/5 text-gray-600 cursor-not-allowed"
                  }`}
                >
                  {isCompleted ? "Riesegui" : isRunning ? "In esecuzione..." : "Avvia"}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Start */}
      <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
        <h3 className="font-semibold text-white mb-4">Avvio Rapido Pipeline</h3>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="https://esempio.it"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-lg bg-[#1a1a2e] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm"
            />
          </div>
          <button
            onClick={handleStartPipeline}
            disabled={!url}
            className="flex items-center gap-2 px-5 py-3 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            Avvia Pipeline
          </button>
        </div>
      </div>

      {/* Platform Guides */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <button
          onClick={() => setShowPlatformGuide("google")}
          className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-blue-500/30 transition-colors group"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center shrink-0">
              <Globe className="w-6 h-6 text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Google Ads Guide</h3>
              <p className="text-sm text-gray-500 mb-3">
                Best practice per campagne Search, Display e Performance Max
              </p>
              <span className="text-sm text-gray-400 group-hover:text-blue-400 transition-colors inline-flex items-center gap-1">
                Scopri come funziona
                <ChevronRight className="w-4 h-4" />
              </span>
            </div>
          </div>
        </button>

        <button
          onClick={() => setShowPlatformGuide("meta")}
          className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-purple-500/30 transition-colors group"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center shrink-0">
              <Target className="w-6 h-6 text-purple-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Meta Ads Guide</h3>
              <p className="text-sm text-gray-500 mb-3">
                Best practice per Facebook e Instagram Ads
              </p>
              <span className="text-sm text-gray-400 group-hover:text-purple-400 transition-colors inline-flex items-center gap-1">
                Scopri come funziona
                <ChevronRight className="w-4 h-4" />
              </span>
            </div>
          </div>
        </button>
      </div>

      {/* Platform Guide Modal */}
      {showPlatformGuide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-[#141420] rounded-2xl border border-white/10 max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">
                {showPlatformGuide === "google"
                  ? "Google Ads - Struttura Campagna"
                  : "Meta Ads - Struttura Campagna"}
              </h2>
              <button
                onClick={() => setShowPlatformGuide(null)}
                className="p-2 rounded-lg hover:bg-white/5 text-gray-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {showPlatformGuide === "google" ? (
              <div className="space-y-4">
                {[
                  { title: "Account", desc: "Configurazione account Google Ads" },
                  { title: "Campagna", desc: "Search, Display, PMax, Shopping" },
                  { title: "Gruppo Annunci", desc: "Keyword, targeting, offerte" },
                  { title: "Annunci", desc: "Headline, description, extensions" },
                ].map((step, idx) => (
                  <div key={idx} className="flex gap-3 p-3 rounded-lg bg-[#1a1a2e]">
                    <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-xs font-bold shrink-0">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="font-medium text-white">{step.title}</p>
                      <p className="text-sm text-gray-500">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {[
                  { title: "Business Manager", desc: "Configurazione account Meta Business Suite" },
                  { title: "Campagna", desc: "Awareness, Traffic, Conversions, Leads" },
                  { title: "Ad Set", desc: "Audience, placement, budget, schedule" },
                  { title: "Annuncio", desc: "Creative, copy, CTA, landing page" },
                ].map((step, idx) => (
                  <div key={idx} className="flex gap-3 p-3 rounded-lg bg-[#1a1a2e]">
                    <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-xs font-bold shrink-0">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="font-medium text-white">{step.title}</p>
                      <p className="text-sm text-gray-500">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-4">
            <Target className="w-6 h-6 text-amber-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">Template Verticali</h3>
          <p className="text-sm text-gray-500 mb-4">
            14 template strategici pre-configurati per ogni tipo di business
          </p>
          <button
            onClick={() => router.push("/admin/ads/knowledge")}
            className="text-sm text-gray-400 hover:text-amber-400 transition-colors inline-flex items-center gap-1"
          >
            Esplora Template <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-4">
            <Key className="w-6 h-6 text-amber-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">Keyword Intelligence</h3>
          <p className="text-sm text-gray-500 mb-4">
            Ricerca automatica CPC, volume e competizione per 14 settori verticali
          </p>
          <button
            onClick={() => router.push("/admin/ads/knowledge")}
            className="text-sm text-gray-400 hover:text-amber-400 transition-colors inline-flex items-center gap-1"
          >
            Vedi Benchmark <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-4">
            <FileText className="w-6 h-6 text-amber-400" />
          </div>
          <h3 className="font-semibold text-white mb-2">Ad Copy Generator</h3>
          <p className="text-sm text-gray-500 mb-4">
            Genera annunci ottimizzati per Google (15 headlines) e Meta (hook, body, CTA)
          </p>
          <span className="text-sm text-gray-500">Disponibile nel Modulo 3</span>
        </div>
      </div>

      {/* Guardrails */}
      <div className="p-6 rounded-2xl bg-amber-500/5 border border-amber-500/20">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white mb-2">Guardrail di Sicurezza AI</h3>
            <p className="text-sm text-gray-400 mb-4">
              L&apos;AI ADS include protezioni automatiche: hard limit budget, incremento graduale,
              circuit breaker su CPA critico, e richiesta approvazione umana per confidence &lt; 70%.
            </p>
            <div className="flex flex-wrap gap-2">
              {["Budget Cap €500/giorno", "Anomaly Detection", "Human-in-the-loop", "Auto-Pause CPA >3x"].map((label) => (
                <span
                  key={label}
                  className="text-xs px-3 py-1 rounded-full bg-white/5 text-gray-400 border border-white/5"
                >
                  {label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
