"use client";

import { useState, useEffect } from "react";
import { API_BASE } from "@/lib/api";
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Search,
  TrendingUp,
  Cpu,
  TrendingDown,
  User,
  Loader2,
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
interface PendingActivity {
  id: string;
  module: "investigator" | "analyst" | "architect" | "broker";
  action: string;
  description: string;
  reasoning?: string;
  confidence?: number;
  createdAt: string;
}

interface Alert {
  id: string;
  type: "critical" | "warning" | "info";
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
}

const moduleIcons: Record<string, typeof Search> = {
  investigator: Search,
  analyst: TrendingUp,
  architect: Cpu,
  broker: TrendingDown,
};

const moduleLabels: Record<string, string> = {
  investigator: "Investigatore",
  analyst: "Analista",
  architect: "Architetto",
  broker: "Broker",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function SupervisionPage() {
  const [pending, setPending] = useState<PendingActivity[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ approvedToday: 0, overrides: 0 });

  useEffect(() => {
    const load = async () => {
      try {
        const data = await adminFetch("/api/ads/supervision");
        setPending(data.pending || []);
        setAlerts(data.alerts || []);
        setStats(data.stats || { approvedToday: 0, overrides: 0 });
      } catch {
        // API not available yet -- use mock data
        setPending([
          {
            id: "1",
            module: "architect",
            action: "Approvazione Strategia",
            description: "Piano pubblicitario pronto per approvazione",
            reasoning: "Template retail selezionato, budget €300/mese, confidence 72%",
            confidence: 72,
            createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          },
          {
            id: "2",
            module: "broker",
            action: "Aumento Budget +50%",
            description: "Richiesta incremento budget campagna",
            reasoning: "CPA stabile €12.50 < target €15 per 14 giorni, confidence 88%",
            confidence: 88,
            createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          },
        ]);
        setAlerts([
          {
            id: "1",
            type: "critical",
            title: "CPA Critico",
            message: "Campagna Studio Bianchi ha CPA €45 vs target €20",
            read: false,
            createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          },
          {
            id: "2",
            type: "warning",
            title: "Fase Apprendimento",
            message: "Campagna ancora in learning phase (3 giorni)",
            read: false,
            createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
          },
          {
            id: "3",
            type: "info",
            title: "Ottimizzazione Automatica",
            message: 'Keyword "pizza roma" pausata per CTR < 1%',
            read: true,
            createdAt: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
          },
        ]);
        setStats({ approvedToday: 24, overrides: 3 });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await adminFetch(`/api/ads/supervision/${id}/approve`, { method: "POST" });
    } catch {
      // silent
    }
    setPending((prev) => prev.filter((p) => p.id !== id));
  };

  const handleReject = async (id: string) => {
    try {
      await adminFetch(`/api/ads/supervision/${id}/reject`, { method: "POST" });
    } catch {
      // silent
    }
    setPending((prev) => prev.filter((p) => p.id !== id));
  };

  const alertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "bg-red-500/10 border-red-500/20";
      case "warning":
        return "bg-amber-500/10 border-amber-500/20";
      case "info":
        return "bg-blue-500/10 border-blue-500/20";
      default:
        return "bg-[#1a1a2e] border-white/5";
    }
  };

  const alertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertTriangle className="w-5 h-5 text-red-400" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case "info":
        return <CheckCircle className="w-5 h-5 text-blue-400" />;
      default:
        return <CheckCircle className="w-5 h-5 text-gray-400" />;
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Supervisione</h1>
          <p className="text-gray-500">Approva decisioni AI e monitora alert</p>
        </div>
        {pending.length > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <Shield className="w-5 h-5 text-amber-400" />
            <span className="text-amber-400 font-medium text-sm">
              {pending.length} in attesa
            </span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{pending.length}</p>
              <p className="text-sm text-gray-500">In Attesa</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {alerts.filter((a) => a.type === "critical").length}
              </p>
              <p className="text-sm text-gray-500">Critici</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.approvedToday}</p>
              <p className="text-sm text-gray-500">Approvati Oggi</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl bg-[#141420] border border-white/5 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <User className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.overrides}</p>
              <p className="text-sm text-gray-500">Override Manuali</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Approvals */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">
          Decisioni in Attesa di Approvazione
        </h2>
        {pending.length === 0 ? (
          <div className="rounded-xl bg-[#141420] border border-white/5 p-8 text-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
            <p className="text-white font-medium">Nessuna decisione in attesa</p>
            <p className="text-gray-500 text-sm">L&apos;AI sta operando autonomamente</p>
          </div>
        ) : (
          <div className="space-y-4">
            {pending.map((activity) => {
              const ModuleIcon = moduleIcons[activity.module] || Cpu;

              return (
                <div
                  key={activity.id}
                  className="rounded-xl bg-[#141420] border border-amber-500/20 p-6"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center shrink-0">
                      <ModuleIcon className="w-6 h-6 text-amber-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-amber-400">
                          {moduleLabels[activity.module] || activity.module}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400">
                          Richiede Approvazione
                        </span>
                      </div>
                      <h3 className="font-semibold text-white text-lg mb-1">
                        {activity.action}
                      </h3>
                      <p className="text-gray-400 mb-3">{activity.description}</p>
                      {activity.reasoning && (
                        <p className="text-sm text-gray-500 mb-3">
                          <span className="text-amber-400">Motivazione:</span>{" "}
                          {activity.reasoning}
                        </p>
                      )}
                      {activity.confidence !== undefined && (
                        <div className="flex items-center gap-2 mb-4">
                          <span className="text-sm text-gray-500">Confidence:</span>
                          <div className="flex-1 max-w-32 h-2 bg-[#1a1a2e] rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                activity.confidence >= 70
                                  ? "bg-emerald-400"
                                  : "bg-amber-400"
                              }`}
                              style={{ width: `${activity.confidence}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-500">
                            {activity.confidence}%
                          </span>
                        </div>
                      )}
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleApprove(activity.id)}
                          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
                        >
                          <CheckCircle className="w-4 h-4" />
                          Approva
                        </button>
                        <button
                          onClick={() => handleReject(activity.id)}
                          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/10 text-white font-medium text-sm hover:bg-white/5 transition-colors"
                        >
                          <XCircle className="w-4 h-4" />
                          Rifiuta
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Alerts */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Alert Sistema</h2>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-xl border ${alertColor(alert.type)} ${
                alert.read ? "opacity-60" : ""
              }`}
            >
              <div className="flex items-start gap-3">
                {alertIcon(alert.type)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-white">{alert.title}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        alert.type === "critical"
                          ? "bg-red-500/10 text-red-400"
                          : alert.type === "warning"
                          ? "bg-amber-500/10 text-amber-400"
                          : "bg-white/5 text-gray-500"
                      }`}
                    >
                      {alert.type}
                    </span>
                    {!alert.read && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400">
                        Nuovo
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-400">{alert.message}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
