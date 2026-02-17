"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Users,
  Megaphone,
  DollarSign,
  TrendingUp,
  Sparkles,
  Plus,
  Play,
  ArrowRight,
  Search,
  BarChart3,
  Lightbulb,
  Rocket,
  Loader2,
  CheckCircle,
  Clock,
  AlertTriangle,
  BookOpen,
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
interface AdsStats {
  activeClients: number;
  activeCampaigns: number;
  monthlyBudget: number;
  avgCtr: number;
  totalLeads: number;
  totalSpent: number;
}

interface ModuleInfo {
  id: string;
  name: string;
  icon: typeof Search;
  status: "idle" | "running" | "completed" | "error";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function AdsDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<AdsStats>({
    activeClients: 0,
    activeCampaigns: 0,
    monthlyBudget: 0,
    avgCtr: 0,
    totalLeads: 0,
    totalSpent: 0,
  });
  const [loading, setLoading] = useState(true);

  const modules: ModuleInfo[] = [
    { id: "investigator", name: "Investigatore", icon: Search, status: "idle" },
    { id: "analyst", name: "Analista", icon: BarChart3, status: "idle" },
    { id: "architect", name: "Architetto", icon: Lightbulb, status: "idle" },
    { id: "broker", name: "Broker", icon: Rocket, status: "idle" },
  ];

  useEffect(() => {
    const load = async () => {
      try {
        const data = await adminFetch("/api/ads/stats/dashboard");
        const d = data.data || data;
        setStats({
          activeClients: d.total_clients ?? d.activeClients ?? 0,
          activeCampaigns: d.active_campaigns ?? d.activeCampaigns ?? 0,
          monthlyBudget: d.total_monthly_budget ?? d.monthlyBudget ?? 0,
          avgCtr: d.avgCtr ?? 0,
          totalLeads: d.total_leads ?? d.totalLeads ?? 0,
          totalSpent: d.total_spent ?? d.totalSpent ?? 0,
        });
      } catch {
        // API not available yet -- use defaults
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const statCards = [
    {
      label: "Clienti Attivi",
      value: stats.activeClients.toString(),
      icon: Users,
      trend: stats.activeClients > 0 ? "Pronto" : "Inizia",
      color: stats.activeClients > 0 ? "text-emerald-400" : "text-gray-500",
    },
    {
      label: "Campagne Attive",
      value: stats.activeCampaigns.toString(),
      icon: Megaphone,
      trend: stats.activeCampaigns > 0 ? "Live" : "Nessuna",
      color: stats.activeCampaigns > 0 ? "text-emerald-400" : "text-gray-500",
    },
    {
      label: "Budget Mese",
      value: stats.monthlyBudget > 0 ? `€${stats.monthlyBudget.toLocaleString()}` : "€0",
      icon: DollarSign,
      trend: stats.monthlyBudget > 0 ? "Attivo" : "In attesa",
      color: stats.monthlyBudget > 0 ? "text-emerald-400" : "text-gray-500",
    },
    {
      label: "CTR Medio",
      value: stats.avgCtr > 0 ? `${stats.avgCtr}%` : "-",
      icon: TrendingUp,
      trend: stats.avgCtr > 0 ? "Performante" : "N/D",
      color: stats.avgCtr > 2 ? "text-emerald-400" : "text-gray-500",
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-500/20 via-[#141420] to-[#0a0a0f] border border-violet-500/20 p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-violet-400" />
            <span className="text-violet-400 text-sm font-medium uppercase tracking-wider">
              AI ADS Ecosystem
            </span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Dashboard Supervisione</h2>
          <p className="text-gray-400 max-w-xl mb-6">
            Monitora l&apos;attivita dell&apos;AI, approva le decisioni critiche e supervisiona le
            campagne dei clienti.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => router.push("/admin/ads/clients")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-500 text-white font-medium text-sm hover:bg-violet-400 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Aggiungi Cliente
            </button>
            <button
              onClick={() => router.push("/admin/ads/ai-modules")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-white/10 text-white font-medium text-sm hover:bg-white/5 transition-colors"
            >
              <Play className="w-4 h-4" />
              Avvia Pipeline AI
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => {
          const Icon = s.icon;
          return (
            <div
              key={i}
              className="rounded-xl bg-[#141420] border border-white/5 p-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-500 text-sm mb-1">{s.label}</p>
                  <p className="text-3xl font-bold text-white">{s.value}</p>
                </div>
                <div className="p-3 rounded-xl bg-[#1a1a2e] text-violet-400">
                  <Icon className="w-6 h-6" />
                </div>
              </div>
              <div className="mt-3">
                <span className={`text-sm font-medium ${s.color}`}>{s.trend}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Module Status */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Stato Moduli AI</h2>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {modules.map((m, idx) => {
            const Icon = m.icon;
            return (
              <div
                key={m.id}
                className="rounded-xl bg-[#141420] border border-white/5 p-5 relative"
              >
                <div className="absolute -top-3 left-5 w-6 h-6 rounded-full bg-[#1a1a2e] border border-white/10 flex items-center justify-center text-xs font-bold text-gray-400">
                  {idx + 1}
                </div>
                <div className="flex items-center gap-3 mt-2 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-[#1a1a2e] flex items-center justify-center">
                    {m.status === "completed" ? (
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                    ) : m.status === "running" ? (
                      <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
                    ) : (
                      <Icon className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-white text-sm">{m.name}</p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        m.status === "completed"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : m.status === "running"
                          ? "bg-violet-500/10 text-violet-400"
                          : "bg-white/5 text-gray-500"
                      }`}
                    >
                      {m.status === "completed"
                        ? "Completato"
                        : m.status === "running"
                        ? "In esecuzione"
                        : "In attesa"}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Empty state for campaigns */}
      <div className="rounded-xl border-2 border-dashed border-white/10 p-12 text-center">
        <div className="w-16 h-16 rounded-full bg-violet-500/10 flex items-center justify-center mx-auto mb-4">
          <Megaphone className="w-8 h-8 text-violet-400" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Nessuna campagna attiva</h3>
        <p className="text-gray-400 max-w-md mx-auto mb-6">
          Inizia creando la tua prima campagna pubblicitaria. L&apos;AI ti guidera passo dopo passo.
        </p>
        <button
          onClick={() => router.push("/admin/ads/clients")}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-500 text-white font-medium text-sm hover:bg-violet-400 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Aggiungi Primo Cliente
        </button>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => router.push("/admin/ads/supervision")}
          className="rounded-xl bg-[#141420] border border-white/5 p-5 text-left hover:border-violet-500/30 transition-colors group"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
              <Clock className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <p className="font-medium text-white group-hover:text-violet-400 transition-colors">
                Supervisione
              </p>
              <p className="text-xs text-gray-500">Decisioni in attesa</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-violet-400 transition-colors" />
        </button>

        <button
          onClick={() => router.push("/admin/ads/knowledge")}
          className="rounded-xl bg-[#141420] border border-white/5 p-5 text-left hover:border-violet-500/30 transition-colors group"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="font-medium text-white group-hover:text-violet-400 transition-colors">
                Knowledge Base
              </p>
              <p className="text-xs text-gray-500">Articoli e benchmark</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-violet-400 transition-colors" />
        </button>

        <button
          onClick={() => router.push("/admin/ads/campaigns")}
          className="rounded-xl bg-[#141420] border border-white/5 p-5 text-left hover:border-violet-500/30 transition-colors group"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="font-medium text-white group-hover:text-violet-400 transition-colors">
                Campagne
              </p>
              <p className="text-xs text-gray-500">Gestisci e monitora</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-violet-400 transition-colors" />
        </button>
      </div>
    </div>
  );
}
