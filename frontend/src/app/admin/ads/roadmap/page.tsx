"use client";

import { useState, useEffect } from "react";
import { API_BASE } from "@/lib/api";
import {
  Loader2,
  CheckCircle,
  Circle,
  Lock,
  Play,
  Target,
  Shield,
  Zap,
  Rocket,
  TrendingUp,
  DollarSign,
  Cpu,
  Network,
  BarChart3,
} from "lucide-react";

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
function adminFetch(path: string) {
  const token = sessionStorage.getItem("admin_token");
  return fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  }).then((res) => {
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  });
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface Prerequisite {
  label: string;
  done: boolean;
  key?: string;
}

interface PhaseTask {
  label: string;
  done: boolean;
}

interface Phase {
  number: number;
  name: string;
  subtitle: string;
  months: string;
  status: "in-corso" | "pianificata";
  icon: typeof Target;
  tasks: PhaseTask[];
}

interface Competitor {
  name: string;
  focus: string;
  strengths: string;
  limitations: string;
  price: string;
}

interface BudgetRow {
  item: string;
  cost: string;
  note: string;
}

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------
const defaultPrerequisites: Prerequisite[] = [
  { label: "Google Ads Developer Token richiesto", done: false, key: "google_dev_token" },
  { label: "Database modelli creati", done: true },
  { label: "Knowledge Base 39+ articoli", done: true },
  { label: "Google Ads API configurata", done: false, key: "google_ads_api" },
  { label: "Meta Marketing API configurata", done: false, key: "meta_api" },
  { label: "DataForSEO configurato", done: false, key: "dataforseo" },
  { label: "n8n workflows creati", done: true },
  { label: "Telegram bot configurato", done: false, key: "telegram_bot" },
  { label: "4 Moduli AI (struttura base)", done: true },
  { label: "Prima campagna test lanciata", done: false },
];

const phases: Phase[] = [
  {
    number: 1,
    name: "FOUNDATION",
    subtitle: "Infrastruttura e basi",
    months: "Mesi 1-2",
    status: "in-corso",
    icon: Target,
    tasks: [
      { label: "Setup infrastruttura", done: true },
      { label: "Pipeline analisi semantica", done: true },
      { label: "Auth OAuth Google", done: false },
      { label: "Dashboard base", done: true },
    ],
  },
  {
    number: 2,
    name: "INTELLIGENCE",
    subtitle: "Dati e intelligenza di mercato",
    months: "Mesi 3-4",
    status: "pianificata",
    icon: BarChart3,
    tasks: [
      { label: "Google Ads API integration", done: false },
      { label: "Market intelligence pipeline", done: false },
      { label: "Knowledge base vettoriale", done: false },
      { label: "Prototipo motore decisionale", done: false },
    ],
  },
  {
    number: 3,
    name: "AUTONOMY",
    subtitle: "Agenti autonomi e guardrails",
    months: "Mesi 5-7",
    status: "pianificata",
    icon: Shield,
    tasks: [
      { label: "Multi-agent system", done: false },
      { label: "Copywriting AI", done: false },
      { label: "Campaign deployment", done: false },
      { label: "Guardrails completi", done: false },
      { label: "Beta test", done: false },
    ],
  },
  {
    number: 4,
    name: "SCALE",
    subtitle: "Espansione e go-to-market",
    months: "Mesi 8-12",
    status: "pianificata",
    icon: Rocket,
    tasks: [
      { label: "A/B testing MAB", done: false },
      { label: "Meta Ads expansion", done: false },
      { label: "Performance Max", done: false },
      { label: "Self-service onboarding", done: false },
      { label: "Go-to-market", done: false },
    ],
  },
];

const competitors: Competitor[] = [
  { name: "Albert.ai", focus: "Ottimizzazione autonoma", strengths: "24/7, cross-channel", limitations: "No strategia/creativita", price: "2-5% ad spend" },
  { name: "ViantAI", focus: "Programmatic", strengths: "4 input = piano", limitations: "Solo programmatic", price: "Enterprise" },
  { name: "AdCreative.ai", focus: "Creativita", strengths: "Veloce, economico", limitations: "Solo generazione", price: "Da $39/mese" },
  { name: "Madgicx", focus: "Meta Ads", strengths: "Workflow Meta", limitations: "Solo Meta", price: "Da $99/mese" },
  { name: "OTTO", focus: "Google Ads auto", strengths: "URL -> campagna", limitations: "Solo Google", price: "Custom" },
  { name: "Optmyzr", focus: "Ottimizzazione Google", strengths: "Rule engine", limitations: "Non autonomo", price: "Da $209/mese" },
];

const budgetRows: BudgetRow[] = [
  { item: "API LLM", cost: "$500 - $2.000", note: "Volume-dependent" },
  { item: "Google/Meta API", cost: "$0", note: "Free (ads spend separato)" },
  { item: "DataForSEO", cost: "$100 - $500", note: "Pay-per-query" },
  { item: "Hosting", cost: "$100 - $500", note: "Railway + Vercel" },
  { item: "Database", cost: "$50 - $200", note: "Supabase + Pinecone" },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function RoadmapPage() {
  const [prerequisites, setPrerequisites] = useState(defaultPrerequisites);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const status = await adminFetch("/api/ads/config/status");
        setPrerequisites((prev) =>
          prev.map((p) => {
            if (p.key && status[p.key] !== undefined) {
              return { ...p, done: !!status[p.key] };
            }
            return p;
          })
        );
      } catch {
        // API not available -- use defaults
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const completedPrereqs = prerequisites.filter((p) => p.done).length;
  const totalPrereqs = prerequisites.length;
  const progressPercent = Math.round((completedPrereqs / totalPrereqs) * 100);

  const currentPhase = 1;
  const overallProgress = Math.round((currentPhase / 4) * 100);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-amber-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Roadmap Progetto</h1>
        <p className="text-gray-400">
          Piano di sviluppo AI ADS - Autonomous Media Buyer
        </p>
      </div>

      {/* ================================================================== */}
      {/* Section 1: Overview Status */}
      {/* ================================================================== */}
      <div className="rounded-2xl bg-[#141420] border border-white/5 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-white">Stato Generale</h2>
            <p className="text-gray-400 text-sm mt-1">
              Fase {currentPhase} di 4 &mdash; Foundation
            </p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <Play className="w-4 h-4 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">In Corso</span>
          </div>
        </div>

        {/* Overall progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-400">Progresso complessivo</span>
            <span className="text-white font-medium">{overallProgress}%</span>
          </div>
          <div className="h-3 bg-[#1a1a2e] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Prerequisites checklist */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium">Checklist Prerequisiti</h3>
            <span className="text-sm text-gray-400">
              {completedPrereqs}/{totalPrereqs} completati
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {prerequisites.map((p, i) => (
              <div
                key={i}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg ${
                  p.done ? "bg-emerald-500/5" : "bg-white/[0.02]"
                }`}
              >
                {p.done ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-600 shrink-0" />
                )}
                <span
                  className={`text-sm ${
                    p.done ? "text-emerald-300" : "text-gray-400"
                  }`}
                >
                  {p.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ================================================================== */}
      {/* Section 2: Le 4 Fasi */}
      {/* ================================================================== */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Le 4 Fasi</h2>
        <div className="space-y-4">
          {phases.map((phase) => {
            const Icon = phase.icon;
            const isActive = phase.status === "in-corso";
            const completedTasks = phase.tasks.filter((t) => t.done).length;
            const taskProgress = Math.round(
              (completedTasks / phase.tasks.length) * 100
            );

            return (
              <div
                key={phase.number}
                className={`rounded-xl border p-5 transition-all ${
                  isActive
                    ? "bg-[#141420] border-amber-500/20"
                    : "bg-[#141420]/50 border-white/5"
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Phase number & icon */}
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                      isActive
                        ? "bg-amber-500/10 text-amber-400"
                        : "bg-white/5 text-gray-500"
                    }`}
                  >
                    {isActive ? (
                      <Icon className="w-6 h-6" />
                    ) : (
                      <Lock className="w-5 h-5" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-white font-semibold">
                        Fase {phase.number} &mdash; {phase.name}
                      </h3>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                          isActive
                            ? "bg-amber-500/10 text-amber-400"
                            : "bg-white/5 text-gray-500"
                        }`}
                      >
                        {isActive ? "In Corso" : "Pianificata"}
                      </span>
                    </div>
                    <p className="text-gray-500 text-sm mb-3">
                      {phase.subtitle} &middot; {phase.months}
                    </p>

                    {/* Task list */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {phase.tasks.map((task, ti) => (
                        <span
                          key={ti}
                          className={`inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg ${
                            task.done
                              ? "bg-emerald-500/10 text-emerald-400"
                              : isActive
                              ? "bg-white/5 text-gray-400"
                              : "bg-white/[0.02] text-gray-600"
                          }`}
                        >
                          {task.done ? (
                            <CheckCircle className="w-3 h-3" />
                          ) : (
                            <Circle className="w-3 h-3" />
                          )}
                          {task.label}
                        </span>
                      ))}
                    </div>

                    {/* Progress bar */}
                    {isActive && (
                      <div>
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-500">
                            {completedTasks}/{phase.tasks.length} completate
                          </span>
                          <span className="text-amber-400">{taskProgress}%</span>
                        </div>
                        <div className="h-1.5 bg-[#1a1a2e] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-amber-500 rounded-full transition-all"
                            style={{ width: `${taskProgress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ================================================================== */}
      {/* Section 3: Analisi Competitor */}
      {/* ================================================================== */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">
          Analisi Competitor
        </h2>
        <div className="rounded-xl bg-[#141420] border border-white/5 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left px-5 py-3 text-gray-400 font-medium">
                    Piattaforma
                  </th>
                  <th className="text-left px-5 py-3 text-gray-400 font-medium">
                    Focus
                  </th>
                  <th className="text-left px-5 py-3 text-gray-400 font-medium">
                    Punti di Forza
                  </th>
                  <th className="text-left px-5 py-3 text-gray-400 font-medium">
                    Limitazioni
                  </th>
                  <th className="text-left px-5 py-3 text-gray-400 font-medium">
                    Prezzo
                  </th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((c, i) => (
                  <tr
                    key={i}
                    className="border-b border-white/5 last:border-0"
                  >
                    <td className="px-5 py-3 text-white font-medium">
                      {c.name}
                    </td>
                    <td className="px-5 py-3 text-gray-300">{c.focus}</td>
                    <td className="px-5 py-3 text-gray-300">{c.strengths}</td>
                    <td className="px-5 py-3 text-gray-400">{c.limitations}</td>
                    <td className="px-5 py-3 text-gray-300">{c.price}</td>
                  </tr>
                ))}
                {/* AI ADS highlighted row */}
                <tr className="bg-amber-500/5 border-t border-amber-500/20">
                  <td className="px-5 py-3 text-amber-400 font-bold">
                    AI ADS
                  </td>
                  <td className="px-5 py-3 text-amber-300 font-medium">
                    End-to-end
                  </td>
                  <td className="px-5 py-3 text-amber-300" colSpan={2}>
                    URL &rarr; Strategia &rarr; Lancio &rarr; Ottimizzazione
                  </td>
                  <td className="px-5 py-3 text-amber-300 font-medium">
                    SaaS
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ================================================================== */}
      {/* Section 4: Budget Estimato */}
      {/* ================================================================== */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">
          <DollarSign className="w-5 h-5 inline-block mr-2 text-amber-400" />
          Budget Stimato MVP
        </h2>
        <div className="rounded-xl bg-[#141420] border border-white/5 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-5 py-3 text-gray-400 font-medium">
                  Voce
                </th>
                <th className="text-left px-5 py-3 text-gray-400 font-medium">
                  Costo Mensile
                </th>
                <th className="text-left px-5 py-3 text-gray-400 font-medium">
                  Note
                </th>
              </tr>
            </thead>
            <tbody>
              {budgetRows.map((b, i) => (
                <tr
                  key={i}
                  className="border-b border-white/5 last:border-0"
                >
                  <td className="px-5 py-3 text-white font-medium">
                    {b.item}
                  </td>
                  <td className="px-5 py-3 text-gray-300">{b.cost}</td>
                  <td className="px-5 py-3 text-gray-400">{b.note}</td>
                </tr>
              ))}
              {/* Total row */}
              <tr className="bg-amber-500/5 border-t border-amber-500/20">
                <td className="px-5 py-3 text-amber-400 font-bold">TOTALE</td>
                <td className="px-5 py-3 text-amber-300 font-bold">
                  $800 - $3.500
                </td>
                <td className="px-5 py-3 text-amber-300">
                  Escluso costi team
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* ================================================================== */}
      {/* Section 5: Elementi Innovativi */}
      {/* ================================================================== */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">
          Elementi Innovativi
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* MCP */}
          <div className="rounded-xl bg-[#141420] border border-white/5 p-5">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
              <Cpu className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">
              MCP (Model Context Protocol)
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Standard per interoperabilita agent-to-SaaS. Permette ai moduli AI
              di comunicare con qualsiasi piattaforma esterna in modo strutturato
              e sicuro.
            </p>
          </div>

          {/* A2A */}
          <div className="rounded-xl bg-[#141420] border border-white/5 p-5">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
              <Network className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">
              Agent-to-Agent Protocol (A2A)
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Coordinazione agenti AI tra sistemi diversi. I 4 moduli comunicano
              tra loro con protocollo strutturato per decisioni collaborative.
            </p>
          </div>

          {/* Topic Velocity */}
          <div className="rounded-xl bg-[#141420] border border-white/5 p-5">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-4">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">
              Topic Velocity Analysis
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Analisi trend emergenti tramite Google Trends API. Identifica
              argomenti in crescita per anticipare la domanda nelle campagne.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
