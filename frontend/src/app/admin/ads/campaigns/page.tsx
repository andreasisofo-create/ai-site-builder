"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Plus,
  Search,
  Filter,
  Play,
  Pause,
  Globe,
  ArrowRight,
  AlertCircle,
  Loader2,
  Instagram,
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
// Types
// ---------------------------------------------------------------------------
interface Campaign {
  id: string;
  name: string;
  platform: "google" | "meta";
  status: "active" | "pending" | "paused" | "completed" | "error";
  budget: { total: number; spent?: number };
  metrics?: {
    impressions?: number;
    clicks?: number;
    ctr?: number;
    conversions?: number;
    cpa?: number;
  };
  externalId?: string;
}

const platformIcons: Record<string, typeof Globe> = {
  google: Globe,
  meta: Instagram,
};

const platformLabels: Record<string, string> = {
  google: "Google Ads",
  meta: "Meta Ads",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function CampaignsPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await adminFetch("/api/ads/campaigns");
        setCampaigns(data.data || data.campaigns || []);
      } catch {
        // API not available yet
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = campaigns.filter((c) => {
    const matchSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchStatus = filterStatus === "all" || c.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const budgetProgress = (spent: number, total: number) => {
    if (!total) return 0;
    return Math.min((spent / total) * 100, 100);
  };

  const statusBadge = (status: string) => {
    const map: Record<string, { label: string; cls: string }> = {
      active: { label: "Attiva", cls: "bg-emerald-500/10 text-emerald-400" },
      pending: { label: "In Attesa", cls: "bg-amber-500/10 text-amber-400" },
      paused: { label: "In Pausa", cls: "bg-white/5 text-gray-400" },
      completed: { label: "Completata", cls: "bg-blue-500/10 text-blue-400" },
      error: { label: "Errore", cls: "bg-red-500/10 text-red-400" },
    };
    const s = map[status] || { label: status, cls: "bg-white/5 text-gray-500" };
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full ${s.cls}`}>{s.label}</span>
    );
  };

  const handlePauseResume = async (id: string, currentStatus: string) => {
    const newStatus = currentStatus === "active" ? "paused" : "active";
    try {
      await adminFetch(`/api/ads/campaigns/${id}/status`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus }),
      });
      setCampaigns((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: newStatus as Campaign["status"] } : c))
      );
    } catch {
      // silent
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-amber-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Campagne</h1>
          <p className="text-gray-500">Gestisci le campagne pubblicitarie attive</p>
        </div>
        <button
          onClick={() => router.push("/admin/ads/wizard")}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nuova Campagna
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Cerca campagna..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-amber-500/50 focus:outline-none"
          >
            <option value="all">Tutti gli stati</option>
            <option value="active">Attive</option>
            <option value="pending">In Attesa</option>
            <option value="paused">In Pausa</option>
            <option value="completed">Completate</option>
            <option value="error">Con Errori</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      {campaigns.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
            <p className="text-gray-500 text-sm">Campagne Attive</p>
            <p className="text-2xl font-bold text-white">
              {campaigns.filter((c) => c.status === "active").length}
            </p>
          </div>
          <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
            <p className="text-gray-500 text-sm">Budget Totale</p>
            <p className="text-2xl font-bold text-white">
              €{campaigns.reduce((a, c) => a + c.budget.total, 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
            <p className="text-gray-500 text-sm">Speso</p>
            <p className="text-2xl font-bold text-white">
              €{campaigns.reduce((a, c) => a + (c.budget.spent || 0), 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
            <p className="text-gray-500 text-sm">CTR Medio</p>
            <p className="text-2xl font-bold text-white">
              {(() => {
                const withCtr = campaigns.filter((c) => c.metrics?.ctr);
                if (!withCtr.length) return "-";
                return (
                  withCtr.reduce((a, c) => a + (c.metrics?.ctr || 0), 0) / withCtr.length
                ).toFixed(2) + "%";
              })()}
            </p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {campaigns.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-white/10 p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Nessuna campagna trovata</h3>
          <p className="text-gray-400 max-w-md mx-auto mb-6">
            Inizia creando la tua prima campagna pubblicitaria. L&apos;AI ti guidera passo dopo
            passo.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => router.push("/admin/ads/wizard")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Crea Prima Campagna
            </button>
            <button
              onClick={() => router.push("/admin/ads/clients")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-white/10 text-white font-medium text-sm hover:bg-white/5 transition-colors"
            >
              Seleziona Cliente
            </button>
          </div>
        </div>
      )}

      {/* Campaign List */}
      <div className="space-y-4">
        {filtered.map((campaign) => {
          const PlatformIcon = platformIcons[campaign.platform] || Globe;
          const bp = budgetProgress(campaign.budget.spent || 0, campaign.budget.total);

          return (
            <div
              key={campaign.id}
              className="rounded-xl bg-[#141420] border border-white/5 p-6 group"
            >
              <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-[#1a1a2e] flex items-center justify-center">
                      <PlatformIcon className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{campaign.name}</h3>
                      <p className="text-xs text-gray-500">
                        {platformLabels[campaign.platform] || campaign.platform}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    {statusBadge(campaign.status)}
                    {campaign.externalId && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-500">
                        ID: {campaign.externalId}
                      </span>
                    )}
                  </div>
                </div>

                {/* Budget */}
                <div className="lg:w-48">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-500">Budget</span>
                    <span className="text-white">
                      €{campaign.budget.spent || 0} / €{campaign.budget.total}
                    </span>
                  </div>
                  <div className="h-2 bg-[#1a1a2e] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        bp > 90
                          ? "bg-red-500"
                          : bp > 70
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${bp}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{bp.toFixed(0)}% utilizzato</p>
                </div>

                {/* Metrics */}
                <div className="flex items-center gap-6">
                  {campaign.status !== "pending" && campaign.metrics && (
                    <>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-white">
                          {(campaign.metrics.impressions || 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">Impressioni</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-white">
                          {(campaign.metrics.clicks || 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">Click</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-amber-400">
                          {campaign.metrics.ctr || 0}%
                        </p>
                        <p className="text-xs text-gray-500">CTR</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-white">
                          {campaign.metrics.conversions || 0}
                        </p>
                        <p className="text-xs text-gray-500">Conv.</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-semibold text-white">
                          €{campaign.metrics.cpa || 0}
                        </p>
                        <p className="text-xs text-gray-500">CPA</p>
                      </div>
                    </>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {campaign.status === "active" && (
                      <button
                        className="p-2 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors"
                        onClick={() => handlePauseResume(campaign.id, campaign.status)}
                        title="Metti in pausa"
                      >
                        <Pause className="w-5 h-5" />
                      </button>
                    )}
                    {campaign.status === "paused" && (
                      <button
                        className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors"
                        onClick={() => handlePauseResume(campaign.id, campaign.status)}
                        title="Riattiva"
                      >
                        <Play className="w-5 h-5" />
                      </button>
                    )}
                    <button
                      className="p-2 rounded-lg bg-[#1a1a2e] hover:bg-white/10 transition-colors"
                      title="Dettagli"
                      onClick={() => router.push(`/admin/ads/campaigns/${campaign.id}`)}
                    >
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
