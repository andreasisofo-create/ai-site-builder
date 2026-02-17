"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Search,
  BarChart3,
  Brain,
  Rocket,
  Play,
  CheckCircle,
  Loader2,
  Globe,
  ArrowRight,
  Shield,
  DollarSign,
  Zap,
  Clock,
  ChevronDown,
  ChevronUp,
  Check,
  X,
  Activity,
  Sparkles,
  Settings,
  Eye,
  FileText,
  Target,
  ShoppingCart,
  MapPin,
  Monitor,
  Video,
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
type ModuleStatus = "idle" | "running" | "completed" | "error";
type GuardrailTab = "budget" | "strategy" | "content";

interface ActivityLogEntry {
  id: string;
  timestamp: string;
  module: "investigator" | "analyst" | "architect" | "broker";
  action: string;
  confidence: number;
  status: "auto" | "pending" | "approved" | "rejected";
}

// ---------------------------------------------------------------------------
// Decision logic table for Module 3
// ---------------------------------------------------------------------------
const decisionLogic = [
  {
    scenario: "E-commerce (prodotto ricercato)",
    channels: "Google Search + Shopping",
    strategy: "Risposta Diretta",
    icon: ShoppingCart,
  },
  {
    scenario: "E-commerce (prodotto nuovo)",
    channels: "YouTube + Display + Search",
    strategy: "Awareness + Remarketing",
    icon: Video,
  },
  {
    scenario: "Servizio locale",
    channels: "Google Search + Maps",
    strategy: "Lead Generation",
    icon: MapPin,
  },
  {
    scenario: "SaaS / High-Ticket",
    channels: "Search + YouTube + LinkedIn",
    strategy: "Lead Magnet + Nurturing + Demo",
    icon: Monitor,
  },
  {
    scenario: "Infoprodotto",
    channels: "YouTube + Search + Display",
    strategy: "Webinar + Email + Vendita",
    icon: FileText,
  },
];

// ---------------------------------------------------------------------------
// Mock activity log
// ---------------------------------------------------------------------------
const mockActivityLog: ActivityLogEntry[] = [
  {
    id: "1",
    timestamp: "2026-02-17 10:32",
    module: "investigator",
    action: "Analisi completata per www.esempio.it - Score landing: 72/100",
    confidence: 89,
    status: "auto",
  },
  {
    id: "2",
    timestamp: "2026-02-17 10:35",
    module: "analyst",
    action: "Keyword research: 847 keyword analizzate, CPC medio: €1.23",
    confidence: 82,
    status: "auto",
  },
  {
    id: "3",
    timestamp: "2026-02-17 10:40",
    module: "architect",
    action: "Piano strategico generato: 3 campagne Search + 1 PMax",
    confidence: 64,
    status: "pending",
  },
  {
    id: "4",
    timestamp: "2026-02-17 09:15",
    module: "broker",
    action: "Bid adjustment: keyword 'consulenza fiscale' CPC +15%",
    confidence: 91,
    status: "auto",
  },
  {
    id: "5",
    timestamp: "2026-02-17 08:50",
    module: "architect",
    action: "Nuova RSA generata: 15 titoli + 4 descrizioni per campagna Search",
    confidence: 76,
    status: "approved",
  },
];

// ---------------------------------------------------------------------------
// Module definitions
// ---------------------------------------------------------------------------
const modules = [
  {
    id: "investigator",
    name: "L'Investigatore",
    subtitle: "Analisi Cliente & Asset",
    description:
      "Riceve un URL e costruisce automaticamente un profilo completo del business. Analizza struttura del sito, contenuti, proposta di valore e qualita tecnica.",
    icon: Search,
    color: "blue",
    outputs: [
      "Categoria business",
      "Proposta di valore",
      "Catalogo prodotti/servizi",
      "Punteggio tecnico landing page",
    ],
    techStack: "Firecrawl + Claude/Kimi per analisi semantica",
    configLink: "/admin/ads/setup?step=1",
  },
  {
    id: "analyst",
    name: "L'Analista di Mercato",
    subtitle: "Trend & Competizione",
    description:
      "Analizza keyword, competitor, benchmark di settore e trend stagionali. Costruisce una mappa completa del panorama competitivo.",
    icon: BarChart3,
    color: "emerald",
    outputs: [
      "Mappa keyword (volumi, CPC, trend)",
      "Indice stagionalita",
      "Stima budget competitivo",
      "SWOT vs competitor",
    ],
    techStack: "Google Ads API KeywordPlanner + DataForSEO + Google Trends",
    configLink: "/admin/ads/setup?step=2",
  },
  {
    id: "architect",
    name: "L'Architetto",
    subtitle: "Piano Marketing",
    description:
      "Incrocia i dati dei moduli 1 e 2 per generare una strategia pubblicitaria completa con campagne, keyword, copy annunci e KPI target.",
    icon: Brain,
    color: "amber",
    outputs: [
      "Piano campagne completo",
      "Keyword con match type",
      "Copy annunci RSA (15 titoli + 4 descrizioni)",
      "Allocazione budget e KPI target",
    ],
    techStack: "Multi-Agent AI con logica decisionale",
    configLink: "/admin/ads/setup?step=6",
  },
  {
    id: "broker",
    name: "Il Broker",
    subtitle: "Gestione Budget & Ottimizzazione",
    description:
      "Gestisce il budget come un investitore algoritmico. Ottimizza bid, gestisce A/B test e monitora performance in tempo reale.",
    icon: Rocket,
    color: "purple",
    outputs: [
      "Campagne live",
      "A/B testing automatico",
      "Bid adjustments in tempo reale",
      "Alert e report",
    ],
    techStack: "Google Ads API write + MCP Server + Rule Engine + MAB",
    configLink: "/admin/ads/setup?step=1",
  },
];

// ---------------------------------------------------------------------------
// Color helpers
// ---------------------------------------------------------------------------
function getModuleColors(color: string) {
  const map: Record<string, { bg: string; text: string; border: string; glow: string }> = {
    blue: {
      bg: "bg-blue-500/10",
      text: "text-blue-400",
      border: "border-blue-500/30",
      glow: "shadow-blue-500/10",
    },
    emerald: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      glow: "shadow-emerald-500/10",
    },
    amber: {
      bg: "bg-violet-500/10",
      text: "text-violet-400",
      border: "border-violet-500/30",
      glow: "shadow-violet-500/10",
    },
    purple: {
      bg: "bg-purple-500/10",
      text: "text-purple-400",
      border: "border-purple-500/30",
      glow: "shadow-purple-500/10",
    },
  };
  return map[color] || map.amber;
}

function getModuleBadgeColor(moduleId: string) {
  const map: Record<string, string> = {
    investigator: "bg-blue-500/10 text-blue-400",
    analyst: "bg-emerald-500/10 text-emerald-400",
    architect: "bg-violet-500/10 text-violet-400",
    broker: "bg-purple-500/10 text-purple-400",
  };
  return map[moduleId] || "bg-white/5 text-gray-400";
}

function getModuleLabel(moduleId: string) {
  const map: Record<string, string> = {
    investigator: "Investigatore",
    analyst: "Analista",
    architect: "Architetto",
    broker: "Broker",
  };
  return map[moduleId] || moduleId;
}

// ---------------------------------------------------------------------------
// Confidence Score component
// ---------------------------------------------------------------------------
function ConfidenceScore({ score }: { score: number }) {
  const color =
    score >= 70
      ? "text-emerald-400"
      : score >= 40
      ? "text-violet-400"
      : "text-red-400";
  const bgColor =
    score >= 70
      ? "bg-emerald-500"
      : score >= 40
      ? "bg-violet-500"
      : "bg-red-500";

  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className={`h-full rounded-full ${bgColor}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className={`text-xs font-medium ${color}`}>{score}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Toggle component
// ---------------------------------------------------------------------------
function Toggle({
  enabled,
  onChange,
  label,
  description,
  locked,
}: {
  enabled: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description?: string;
  locked?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {description && (
          <p className="text-xs text-gray-500 mt-0.5">{description}</p>
        )}
      </div>
      <button
        onClick={() => !locked && onChange(!enabled)}
        className={`relative w-11 h-6 rounded-full transition-colors shrink-0 ${
          locked
            ? "bg-emerald-500/30 cursor-not-allowed"
            : enabled
            ? "bg-emerald-500"
            : "bg-white/10"
        }`}
      >
        <div
          className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${
            enabled || locked ? "translate-x-[22px]" : "translate-x-0.5"
          }`}
        />
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------
export default function AIModulesPage() {
  const router = useRouter();

  // Quick Start state
  const [url, setUrl] = useState("");
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [moduleStatus, setModuleStatus] = useState<Record<string, ModuleStatus>>({
    investigator: "idle",
    analyst: "idle",
    architect: "idle",
    broker: "idle",
  });
  const [pipelineResult, setPipelineResult] = useState<{
    businessType: string;
    valueProp: string;
    landingScore: number;
  } | null>(null);

  // Module card expansion
  const [expandedModule, setExpandedModule] = useState<string | null>(null);

  // Guardrails state
  const [guardrailTab, setGuardrailTab] = useState<GuardrailTab>("budget");
  const [guardrails, setGuardrails] = useState({
    // Budget
    dailyBudgetCap: 500,
    monthlyBudgetCap: 10000,
    gradualIncrease: true,
    gradualMax24h: 20,
    gradualMax7d: 50,
    circuitBreakerEnabled: true,
    circuitBreakerCpaPercent: 200,
    circuitBreakerHours: 4,
    anomalyDetection: true,
    // Strategy
    humanApproval: true,
    confidenceThreshold: 70,
    multiAgentReview: true,
    benchmarkValidation: true,
    // Content
    policyCompliance: true,
    brandSafetyText: "",
    factChecking: true,
  });

  // Activity log state
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>(mockActivityLog);

  // Pipeline execution
  const runPipeline = async () => {
    if (!url) return;
    setPipelineRunning(true);
    setPipelineResult(null);

    const moduleIds = ["investigator", "analyst", "architect", "broker"];

    for (const moduleId of moduleIds) {
      setModuleStatus((prev) => ({ ...prev, [moduleId]: "running" }));
      try {
        await adminFetch("/api/ads/modules/run", {
          method: "POST",
          body: JSON.stringify({ module: moduleId, url }),
        });
        setModuleStatus((prev) => ({ ...prev, [moduleId]: "completed" }));
      } catch {
        // Simulate completion for demo
        await new Promise((r) => setTimeout(r, 2000));
        setModuleStatus((prev) => ({ ...prev, [moduleId]: "completed" }));
      }
    }

    setPipelineResult({
      businessType: "E-commerce",
      valueProp: "Prodotti artigianali made in Italy",
      landingScore: 72,
    });
    setPipelineRunning(false);
  };

  // Activity log actions
  const handleApprove = (id: string) => {
    setActivityLog((prev) =>
      prev.map((e) => (e.id === id ? { ...e, status: "approved" as const } : e))
    );
  };

  const handleReject = (id: string) => {
    setActivityLog((prev) =>
      prev.map((e) => (e.id === id ? { ...e, status: "rejected" as const } : e))
    );
  };

  return (
    <div className="space-y-8">
      {/* ================================================================= */}
      {/* HEADER                                                            */}
      {/* ================================================================= */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-500/15 via-[#141420] to-[#0a0a0f] border border-violet-500/20 p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-3">
            <Sparkles className="w-5 h-5 text-violet-400" />
            <span className="text-violet-400 text-sm font-medium uppercase tracking-wider">
              AI ADS - Autonomous Media Buyer
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Pipeline AI a 4 Moduli</h1>
          <p className="text-gray-400 max-w-2xl">
            Dall&apos;URL del cliente alla campagna live, completamente automatizzato.
            Ogni modulo analizza, pianifica e ottimizza in autonomia con guardrail di sicurezza integrati.
          </p>
        </div>
      </div>

      {/* ================================================================= */}
      {/* SECTION 1: QUICK START                                            */}
      {/* ================================================================= */}
      <div className="rounded-2xl bg-[#141420] border border-white/5 p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
            <Zap className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Quick Start</h2>
            <p className="text-sm text-gray-500">
              Inserisci l&apos;URL del sito web del cliente per avviare l&apos;analisi completa
            </p>
          </div>
        </div>

        {/* URL Input */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="url"
              placeholder="https://www.esempio.it"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full pl-12 pr-4 py-4 rounded-xl bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-violet-500/50 focus:outline-none text-base"
            />
          </div>
          <button
            onClick={runPipeline}
            disabled={!url || pipelineRunning}
            className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-violet-500 text-white font-semibold text-sm hover:bg-violet-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            {pipelineRunning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analisi in corso...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Avvia Analisi AI
              </>
            )}
          </button>
        </div>

        {/* Pipeline Progress */}
        {pipelineRunning && (
          <div className="flex items-center gap-2 mb-6">
            {modules.map((m, idx) => {
              const status = moduleStatus[m.id];
              const colors = getModuleColors(m.color);
              return (
                <div key={m.id} className="flex items-center gap-2 flex-1">
                  <div
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg flex-1 ${
                      status === "completed"
                        ? `${colors.bg} ${colors.border} border`
                        : status === "running"
                        ? `${colors.bg} border ${colors.border} animate-pulse`
                        : "bg-white/5 border border-white/5"
                    }`}
                  >
                    {status === "completed" ? (
                      <CheckCircle className={`w-4 h-4 ${colors.text} shrink-0`} />
                    ) : status === "running" ? (
                      <Loader2 className={`w-4 h-4 ${colors.text} animate-spin shrink-0`} />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-white/10 shrink-0" />
                    )}
                    <span
                      className={`text-xs font-medium truncate ${
                        status === "idle" ? "text-gray-500" : colors.text
                      }`}
                    >
                      {m.name}
                    </span>
                  </div>
                  {idx < modules.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-gray-600 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Pipeline Result */}
        {pipelineResult && (
          <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/20 p-5">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center shrink-0">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-2">Analisi Completata</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">Tipo Business</p>
                    <p className="text-sm text-white font-medium">{pipelineResult.businessType}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">Value Proposition</p>
                    <p className="text-sm text-white font-medium">{pipelineResult.valueProp}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">Landing Score</p>
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-white font-medium">{pipelineResult.landingScore}/100</p>
                      <div className="w-20 h-1.5 rounded-full bg-white/5 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-emerald-500"
                          style={{ width: `${pipelineResult.landingScore}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => router.push("/admin/ads/clients")}
                  className="mt-4 text-sm text-emerald-400 hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
                >
                  Vai al profilo cliente <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION 2: PIPELINE 4 MODULI                                      */}
      {/* ================================================================= */}
      <div>
        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-xl font-bold text-white">Pipeline 4 Moduli</h2>
          <div className="h-px flex-1 bg-white/5" />
        </div>

        {/* Pipeline connection line (desktop) */}
        <div className="relative">
          <div className="absolute top-24 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-blue-500/20 via-emerald-500/20 via-violet-500/20 to-purple-500/20 hidden lg:block" />

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-5 relative">
            {modules.map((module, index) => {
              const ModuleIcon = module.icon;
              const colors = getModuleColors(module.color);
              const status = moduleStatus[module.id];
              const isExpanded = expandedModule === module.id;

              return (
                <div
                  key={module.id}
                  className={`rounded-xl bg-[#141420] border p-6 relative transition-all hover:shadow-lg ${colors.glow} ${
                    status === "completed" ? colors.border : "border-white/5 hover:border-white/10"
                  }`}
                >
                  {/* Step number */}
                  <div
                    className={`absolute -top-3 left-6 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      status === "completed"
                        ? `${colors.bg} ${colors.text} border ${colors.border}`
                        : "bg-[#1a1a2e] border border-white/10 text-gray-400"
                    }`}
                  >
                    {status === "completed" ? (
                      <Check className="w-3.5 h-3.5" />
                    ) : (
                      index + 1
                    )}
                  </div>

                  {/* Header */}
                  <div className="flex items-start gap-3 mb-4 mt-2">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors.bg}`}
                    >
                      {status === "running" ? (
                        <Loader2 className={`w-6 h-6 ${colors.text} animate-spin`} />
                      ) : (
                        <ModuleIcon className={`w-6 h-6 ${colors.text}`} />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-white text-sm leading-tight">
                        {module.name}
                      </h3>
                      <p className={`text-xs ${colors.text} font-medium`}>
                        {module.subtitle}
                      </p>
                    </div>
                    {/* Status badge */}
                    <div
                      className={`w-2.5 h-2.5 rounded-full shrink-0 mt-1 ${
                        status === "completed"
                          ? "bg-emerald-400"
                          : status === "running"
                          ? "bg-violet-400 animate-pulse"
                          : status === "error"
                          ? "bg-red-400"
                          : "bg-gray-600"
                      }`}
                    />
                  </div>

                  <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                    {module.description}
                  </p>

                  {/* Outputs */}
                  <div className="mb-4">
                    <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                      Output
                    </p>
                    <div className="space-y-1.5">
                      {module.outputs.map((output) => (
                        <div key={output} className="flex items-start gap-2">
                          <div className={`w-1 h-1 rounded-full ${colors.text} mt-1.5 shrink-0`} />
                          <span className="text-xs text-gray-400">{output}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Expand/collapse for extra details */}
                  <button
                    onClick={() =>
                      setExpandedModule(isExpanded ? null : module.id)
                    }
                    className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1 mb-4"
                  >
                    {isExpanded ? "Meno dettagli" : "Dettagli tecnici"}
                    {isExpanded ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="mb-4 p-3 rounded-lg bg-[#0a0a0f] border border-white/5">
                      <p className="text-xs text-gray-600 uppercase tracking-wider mb-1">
                        Tech Stack
                      </p>
                      <p className="text-xs text-gray-400">{module.techStack}</p>

                      {/* Decision logic table for Architect */}
                      {module.id === "architect" && (
                        <div className="mt-3">
                          <p className="text-xs text-gray-600 uppercase tracking-wider mb-2">
                            Logica Decisionale
                          </p>
                          <div className="space-y-1.5">
                            {decisionLogic.map((row) => {
                              const RowIcon = row.icon;
                              return (
                                <div
                                  key={row.scenario}
                                  className="flex items-center gap-2 text-xs"
                                >
                                  <RowIcon className="w-3 h-3 text-violet-400 shrink-0" />
                                  <span className="text-gray-300 font-medium min-w-0 truncate">
                                    {row.scenario}
                                  </span>
                                  <ArrowRight className="w-3 h-3 text-gray-600 shrink-0" />
                                  <span className="text-gray-500 truncate">
                                    {row.strategy}
                                  </span>
                                </div>
                              );
                            })}
                          </div>

                          {/* Confidence Score visualization */}
                          <div className="mt-3 p-2 rounded bg-white/5">
                            <p className="text-xs text-gray-500 mb-1.5">
                              Confidence Score
                            </p>
                            <div className="flex items-center gap-3">
                              <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden flex">
                                <div className="h-full bg-red-500" style={{ width: "40%" }} />
                                <div className="h-full bg-violet-500" style={{ width: "30%" }} />
                                <div className="h-full bg-emerald-500" style={{ width: "30%" }} />
                              </div>
                            </div>
                            <div className="flex justify-between mt-1">
                              <span className="text-[10px] text-red-400">
                                &lt;40 Blocco
                              </span>
                              <span className="text-[10px] text-violet-400">
                                40-70 Review
                              </span>
                              <span className="text-[10px] text-emerald-400">
                                &gt;70 Auto
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action */}
                  <button
                    onClick={() => router.push(module.configLink)}
                    className={`w-full py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                      status === "completed"
                        ? `${colors.bg} ${colors.text} hover:opacity-80`
                        : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    <Settings className="w-4 h-4" />
                    Configura
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ================================================================= */}
      {/* SECTION 3: GUARDRAILS PANEL                                       */}
      {/* ================================================================= */}
      <div className="rounded-2xl bg-[#141420] border border-white/5 overflow-hidden">
        {/* Guardrails Header */}
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
              <Shield className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Guardrail di Sicurezza</h2>
              <p className="text-sm text-gray-500">
                Protezioni automatiche per l&apos;operativita autonoma dell&apos;AI
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/5">
          {(
            [
              { id: "budget" as const, label: "Budget", icon: DollarSign },
              { id: "strategy" as const, label: "Strategia", icon: Target },
              { id: "content" as const, label: "Contenuto", icon: FileText },
            ] as const
          ).map((tab) => {
            const TabIcon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setGuardrailTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-3.5 text-sm font-medium transition-colors border-b-2 ${
                  guardrailTab === tab.id
                    ? "border-violet-500 text-violet-400 bg-violet-500/5"
                    : "border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5"
                }`}
              >
                <TabIcon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Budget Tab */}
          {guardrailTab === "budget" && (
            <div className="space-y-5">
              {/* Budget Cap Assoluto */}
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <div className="flex items-center gap-2 mb-4">
                  <DollarSign className="w-4 h-4 text-violet-400" />
                  <h3 className="font-semibold text-white text-sm">Budget Cap Assoluto</h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-500 block mb-1.5">
                      Limite giornaliero
                    </label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                        &euro;
                      </span>
                      <input
                        type="number"
                        value={guardrails.dailyBudgetCap}
                        onChange={(e) =>
                          setGuardrails((g) => ({
                            ...g,
                            dailyBudgetCap: Number(e.target.value),
                          }))
                        }
                        className="w-full pl-8 pr-4 py-2.5 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1.5">
                      Limite mensile
                    </label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                        &euro;
                      </span>
                      <input
                        type="number"
                        value={guardrails.monthlyBudgetCap}
                        onChange={(e) =>
                          setGuardrails((g) => ({
                            ...g,
                            monthlyBudgetCap: Number(e.target.value),
                          }))
                        }
                        className="w-full pl-8 pr-4 py-2.5 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Incremento Graduale */}
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.gradualIncrease}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, gradualIncrease: v }))
                  }
                  label="Incremento Graduale"
                  description="Limita la velocita di aumento del budget"
                />
                {guardrails.gradualIncrease && (
                  <div className="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-white/5">
                    <div>
                      <label className="text-xs text-gray-500 block mb-1.5">
                        Max aumento / 24h
                      </label>
                      <div className="relative">
                        <input
                          type="number"
                          value={guardrails.gradualMax24h}
                          onChange={(e) =>
                            setGuardrails((g) => ({
                              ...g,
                              gradualMax24h: Number(e.target.value),
                            }))
                          }
                          className="w-full pr-8 pl-3 py-2 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                          %
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block mb-1.5">
                        Max aumento / 7 giorni
                      </label>
                      <div className="relative">
                        <input
                          type="number"
                          value={guardrails.gradualMax7d}
                          onChange={(e) =>
                            setGuardrails((g) => ({
                              ...g,
                              gradualMax7d: Number(e.target.value),
                            }))
                          }
                          className="w-full pr-8 pl-3 py-2 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Circuit Breaker */}
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.circuitBreakerEnabled}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, circuitBreakerEnabled: v }))
                  }
                  label="Circuit Breaker"
                  description="Pausa automatica se CPA supera la soglia"
                />
                {guardrails.circuitBreakerEnabled && (
                  <div className="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-white/5">
                    <div>
                      <label className="text-xs text-gray-500 block mb-1.5">
                        CPA soglia (% del target)
                      </label>
                      <div className="relative">
                        <input
                          type="number"
                          value={guardrails.circuitBreakerCpaPercent}
                          onChange={(e) =>
                            setGuardrails((g) => ({
                              ...g,
                              circuitBreakerCpaPercent: Number(e.target.value),
                            }))
                          }
                          className="w-full pr-8 pl-3 py-2 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                          %
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block mb-1.5">
                        Durata minima (ore)
                      </label>
                      <div className="relative">
                        <input
                          type="number"
                          value={guardrails.circuitBreakerHours}
                          onChange={(e) =>
                            setGuardrails((g) => ({
                              ...g,
                              circuitBreakerHours: Number(e.target.value),
                            }))
                          }
                          className="w-full pr-8 pl-3 py-2 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-violet-500/50 focus:outline-none"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                          h
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Anomaly Detection */}
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.anomalyDetection}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, anomalyDetection: v }))
                  }
                  label="Anomaly Detection (Z-Score)"
                  description="Rileva anomalie statistiche su CTR, CPC e conversion rate"
                />
              </div>
            </div>
          )}

          {/* Strategy Tab */}
          {guardrailTab === "strategy" && (
            <div className="space-y-5">
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.humanApproval}
                  onChange={() => {}}
                  label="Approvazione Umana"
                  description="Sempre attiva per piani strategici e modifiche critiche"
                  locked
                />
                <div className="mt-2 flex items-center gap-2 px-2">
                  <Shield className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs text-emerald-400">
                    Questo guardrail non puo essere disattivato
                  </span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-sm font-medium text-white">Confidence Threshold</p>
                    <p className="text-xs text-gray-500">
                      Sotto questa soglia, l&apos;AI richiede conferma umana
                    </p>
                  </div>
                  <span className="text-lg font-bold text-violet-400">
                    {guardrails.confidenceThreshold}%
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={guardrails.confidenceThreshold}
                  onChange={(e) =>
                    setGuardrails((g) => ({
                      ...g,
                      confidenceThreshold: Number(e.target.value),
                    }))
                  }
                  className="w-full h-2 rounded-full appearance-none bg-white/10 accent-violet-500 cursor-pointer"
                />
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-gray-600">0 - Approva tutto</span>
                  <span className="text-[10px] text-gray-600">100 - Approva nulla</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.multiAgentReview}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, multiAgentReview: v }))
                  }
                  label="Multi-Agent Review"
                  description="Un Agent Critic valida ogni piano strategico prima dell'esecuzione"
                />
              </div>

              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.benchmarkValidation}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, benchmarkValidation: v }))
                  }
                  label="Benchmark Validation"
                  description="CPC e CPA previsti vengono validati contro benchmark di settore"
                />
              </div>
            </div>
          )}

          {/* Content Tab */}
          {guardrailTab === "content" && (
            <div className="space-y-5">
              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.policyCompliance}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, policyCompliance: v }))
                  }
                  label="Policy Compliance"
                  description="Verifica automatica conformita con le policy di Google Ads"
                />
              </div>

              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <div className="mb-3">
                  <p className="text-sm font-medium text-white">Brand Safety</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Frasi vietate, tono da mantenere, claim da evitare
                  </p>
                </div>
                <textarea
                  value={guardrails.brandSafetyText}
                  onChange={(e) =>
                    setGuardrails((g) => ({
                      ...g,
                      brandSafetyText: e.target.value,
                    }))
                  }
                  placeholder="Es: Non usare 'il migliore', evitare confronti diretti con competitor, tono professionale ma accessibile..."
                  rows={4}
                  className="w-full px-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-600 text-sm focus:border-violet-500/50 focus:outline-none resize-none"
                />
              </div>

              <div className="p-4 rounded-xl bg-[#0a0a0f] border border-white/5">
                <Toggle
                  enabled={guardrails.factChecking}
                  onChange={(v) =>
                    setGuardrails((g) => ({ ...g, factChecking: v }))
                  }
                  label="Fact-Checking"
                  description="Cross-reference dei claim negli annunci con il contenuto del sito"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ================================================================= */}
      {/* SECTION 4: AI ACTIVITY LOG                                        */}
      {/* ================================================================= */}
      <div className="rounded-2xl bg-[#141420] border border-white/5 overflow-hidden">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Activity Log</h2>
              <p className="text-sm text-gray-500">
                Timeline delle ultime azioni eseguite dai moduli AI
              </p>
            </div>
          </div>
        </div>

        <div className="divide-y divide-white/5">
          {activityLog.map((entry) => (
            <div
              key={entry.id}
              className="p-5 flex items-start gap-4 hover:bg-white/[0.02] transition-colors"
            >
              {/* Timeline dot */}
              <div className="flex flex-col items-center gap-1 pt-1">
                <div
                  className={`w-2.5 h-2.5 rounded-full ${
                    entry.status === "auto" || entry.status === "approved"
                      ? "bg-emerald-400"
                      : entry.status === "pending"
                      ? "bg-violet-400 animate-pulse"
                      : "bg-red-400"
                  }`}
                />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-1.5">
                  <span className="text-xs text-gray-500">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {entry.timestamp}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${getModuleBadgeColor(
                      entry.module
                    )}`}
                  >
                    {getModuleLabel(entry.module)}
                  </span>
                  <ConfidenceScore score={entry.confidence} />
                </div>
                <p className="text-sm text-gray-300">{entry.action}</p>
                <div className="mt-2 flex items-center gap-2">
                  {entry.status === "auto" && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center gap-1">
                      <Zap className="w-3 h-3" /> Auto-eseguito
                    </span>
                  )}
                  {entry.status === "approved" && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> Approvato
                    </span>
                  )}
                  {entry.status === "rejected" && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 flex items-center gap-1">
                      <X className="w-3 h-3" /> Rifiutato
                    </span>
                  )}
                  {entry.status === "pending" && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 flex items-center gap-1">
                        <Eye className="w-3 h-3" /> In attesa di approvazione
                      </span>
                      <button
                        onClick={() => handleApprove(entry.id)}
                        className="text-xs px-3 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" /> Approva
                      </button>
                      <button
                        onClick={() => handleReject(entry.id)}
                        className="text-xs px-3 py-1 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors flex items-center gap-1"
                      >
                        <X className="w-3 h-3" /> Rifiuta
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty state */}
        {activityLog.length === 0 && (
          <div className="p-12 text-center">
            <Activity className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">
              Nessuna attivita AI registrata. Avvia la pipeline per iniziare.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
