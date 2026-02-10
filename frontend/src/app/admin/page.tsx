"use client";

import { useState, useEffect, useCallback, useMemo, Fragment } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AdminStats {
  users: { total: number; active: number; premium: number; recent_30d: number };
  sites: { total: number; published: number; ready: number; generating: number };
  plans: { free: number; base: number; premium: number };
  generations_total: number;
}

interface UserRecord {
  id: number;
  email: string;
  full_name: string | null;
  plan: string;
  is_premium: boolean;
  is_active: boolean;
  sites_count: number;
  generations_used: number;
  created_at: string;
  last_login: string | null;
  sites?: SiteRecord[];
}

interface SiteRecord {
  id: number;
  name: string;
  status: string;
  is_published: boolean;
  template_category: string | null;
  template_style: string | null;
  created_at: string;
  updated_at: string;
  owner_email?: string;
  owner_name?: string;
  user_id?: number;
  html_content?: string;
  published_url?: string | null;
}

interface PaginatedUsers {
  users: UserRecord[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

interface PaginatedSites {
  sites: SiteRecord[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://ai-site-builder-jz2g.onrender.com";

async function adminFetch(path: string, options: RequestInit = {}) {
  const token = sessionStorage.getItem("admin_token");
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (res.status === 401) {
    sessionStorage.removeItem("admin_token");
    throw new Error("SESSION_EXPIRED");
  }
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string | null): string {
  if (!iso) return "---";
  const d = new Date(iso);
  return d.toLocaleDateString("it-IT", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(iso: string | null): string {
  if (!iso) return "---";
  const d = new Date(iso);
  return d.toLocaleDateString("it-IT", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function timeAgo(iso: string | null): string {
  if (!iso) return "mai";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "adesso";
  if (mins < 60) return `${mins}m fa`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h fa`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}g fa`;
  const months = Math.floor(days / 30);
  return `${months}mo fa`;
}

function classNames(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

// ---------------------------------------------------------------------------
// Badge components
// ---------------------------------------------------------------------------

function PlanBadge({ plan }: { plan: string }) {
  const colors: Record<string, string> = {
    free: "bg-gray-700 text-gray-300",
    base: "bg-blue-900/60 text-blue-300",
    premium: "bg-purple-900/60 text-purple-300",
  };
  return (
    <span
      className={classNames(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize",
        colors[plan] || "bg-gray-700 text-gray-300"
      )}
    >
      {plan}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    ready: "bg-green-900/50 text-green-400 border-green-800",
    active: "bg-green-900/50 text-green-400 border-green-800",
    published: "bg-blue-900/50 text-blue-400 border-blue-800",
    generating: "bg-yellow-900/50 text-yellow-400 border-yellow-800",
    pending: "bg-yellow-900/50 text-yellow-400 border-yellow-800",
    draft: "bg-red-900/50 text-red-400 border-red-800",
    inactive: "bg-red-900/50 text-red-400 border-red-800",
    error: "bg-red-900/50 text-red-400 border-red-800",
  };
  return (
    <span
      className={classNames(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize border",
        map[status] || "bg-gray-800 text-gray-400 border-gray-700"
      )}
    >
      {status}
    </span>
  );
}

function BoolBadge({ value, trueLabel = "Si", falseLabel = "No" }: { value: boolean; trueLabel?: string; falseLabel?: string }) {
  return (
    <span
      className={classNames(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
        value
          ? "bg-green-900/50 text-green-400"
          : "bg-gray-800 text-gray-500"
      )}
    >
      {value ? trueLabel : falseLabel}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Shared tiny components
// ---------------------------------------------------------------------------

function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const s = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-5 w-5";
  return (
    <svg
      className={classNames("animate-spin text-indigo-400", s)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={classNames(
        "bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl",
        className
      )}
    >
      {children}
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  accent = false,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <Card className="p-5">
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p
        className={classNames(
          "text-3xl font-bold tracking-tight",
          accent ? "text-indigo-400" : "text-white"
        )}
      >
        {value}
      </p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </Card>
  );
}

function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Elimina",
  onConfirm,
  onCancel,
  loading = false,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-sm rounded-lg bg-[#2a2a2a] text-gray-300 hover:bg-[#333] transition-colors disabled:opacity-50"
          >
            Annulla
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="px-4 py-2 text-sm rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading && <Spinner size="sm" />}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

function Pagination({
  page,
  pages,
  onPage,
}: {
  page: number;
  pages: number;
  onPage: (p: number) => void;
}) {
  if (pages <= 1) return null;
  const range: number[] = [];
  const start = Math.max(1, page - 2);
  const end = Math.min(pages, page + 2);
  for (let i = start; i <= end; i++) range.push(i);

  return (
    <div className="flex items-center gap-1 mt-4 justify-center">
      <button
        disabled={page <= 1}
        onClick={() => onPage(page - 1)}
        className="px-3 py-1.5 text-xs rounded-lg bg-[#2a2a2a] text-gray-400 hover:bg-[#333] disabled:opacity-30 transition-colors"
      >
        Prec
      </button>
      {start > 1 && (
        <>
          <button
            onClick={() => onPage(1)}
            className="px-3 py-1.5 text-xs rounded-lg bg-[#2a2a2a] text-gray-400 hover:bg-[#333] transition-colors"
          >
            1
          </button>
          {start > 2 && <span className="text-gray-600 px-1">...</span>}
        </>
      )}
      {range.map((p) => (
        <button
          key={p}
          onClick={() => onPage(p)}
          className={classNames(
            "px-3 py-1.5 text-xs rounded-lg transition-colors",
            p === page
              ? "bg-indigo-600 text-white"
              : "bg-[#2a2a2a] text-gray-400 hover:bg-[#333]"
          )}
        >
          {p}
        </button>
      ))}
      {end < pages && (
        <>
          {end < pages - 1 && <span className="text-gray-600 px-1">...</span>}
          <button
            onClick={() => onPage(pages)}
            className="px-3 py-1.5 text-xs rounded-lg bg-[#2a2a2a] text-gray-400 hover:bg-[#333] transition-colors"
          >
            {pages}
          </button>
        </>
      )}
      <button
        disabled={page >= pages}
        onClick={() => onPage(page + 1)}
        className="px-3 py-1.5 text-xs rounded-lg bg-[#2a2a2a] text-gray-400 hover:bg-[#333] disabled:opacity-30 transition-colors"
      >
        Succ
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// LOGIN SCREEN
// ---------------------------------------------------------------------------

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || "Credenziali non valide");
      }
      const data = await res.json();
      sessionStorage.setItem("admin_token", data.access_token);
      onLogin();
    } catch (err: any) {
      setError(err.message || "Errore di connessione");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo / Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 mb-4">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">E-quipe Admin</h1>
          <p className="text-sm text-gray-500 mt-1">Pannello di Amministrazione</p>
        </div>

        {/* Form */}
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
                className="w-full px-3 py-2.5 rounded-lg bg-[#0a0a0a] border border-[#2a2a2a] text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                placeholder="Inserisci username"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-3 py-2.5 rounded-lg bg-[#0a0a0a] border border-[#2a2a2a] text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                placeholder="Inserisci password"
              />
            </div>

            {error && (
              <div className="text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-lg p-3">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-[#1a1a1a] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && <Spinner size="sm" />}
              {loading ? "Accesso in corso..." : "Accedi"}
            </button>
          </form>
        </Card>

        <p className="text-center text-xs text-gray-700 mt-6">
          Area riservata &middot; Accesso non autorizzato vietato
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// TAB: OVERVIEW
// ---------------------------------------------------------------------------

function OverviewTab() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await adminFetch("/api/admin/stats");
      setStats(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 mb-4">Errore: {error}</p>
        <button
          onClick={load}
          className="px-4 py-2 text-sm rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
        >
          Riprova
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const planTotal = stats.plans.free + stats.plans.base + stats.plans.premium || 1;
  const planData = [
    {
      label: "Free",
      count: stats.plans.free,
      pct: Math.round((stats.plans.free / planTotal) * 100),
      color: "bg-gray-500",
    },
    {
      label: "Base",
      count: stats.plans.base,
      pct: Math.round((stats.plans.base / planTotal) * 100),
      color: "bg-blue-500",
    },
    {
      label: "Premium",
      count: stats.plans.premium,
      pct: Math.round((stats.plans.premium / planTotal) * 100),
      color: "bg-purple-500",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Utenti Totali" value={stats.users.total} sub={`${stats.users.recent_30d} ultimi 30g`} />
        <StatCard label="Utenti Premium" value={stats.users.premium} sub={`${stats.users.active} attivi`} accent />
        <StatCard label="Siti Totali" value={stats.sites.total} sub={`${stats.sites.published} pubblicati`} />
        <StatCard label="Generazioni" value={stats.generations_total} sub={`${stats.sites.generating} in corso`} accent />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Plan distribution */}
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Distribuzione Piani</h3>
          <div className="space-y-3">
            {planData.map((p) => (
              <div key={p.label}>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>{p.label}</span>
                  <span>
                    {p.count} ({p.pct}%)
                  </span>
                </div>
                <div className="w-full h-3 bg-[#2a2a2a] rounded-full overflow-hidden">
                  <div
                    className={classNames("h-full rounded-full transition-all duration-700", p.color)}
                    style={{ width: `${p.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Sites breakdown */}
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Stato Siti</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Pronti", value: stats.sites.ready, dot: "bg-green-400" },
              { label: "In generazione", value: stats.sites.generating, dot: "bg-yellow-400" },
              { label: "Pubblicati", value: stats.sites.published, dot: "bg-blue-400" },
              {
                label: "Bozza / Altro",
                value: Math.max(
                  0,
                  stats.sites.total -
                    stats.sites.ready -
                    stats.sites.generating -
                    stats.sites.published
                ),
                dot: "bg-red-400",
              },
            ].map((s) => (
              <div
                key={s.label}
                className="flex items-center gap-3 bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a]"
              >
                <span className={classNames("w-2.5 h-2.5 rounded-full flex-shrink-0", s.dot)} />
                <div>
                  <p className="text-lg font-bold text-white leading-none">{s.value}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Quick metrics */}
      <Card className="p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Metriche Rapide</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-white">
              {stats.users.total > 0
                ? (stats.sites.total / stats.users.total).toFixed(1)
                : "0"}
            </p>
            <p className="text-xs text-gray-500 mt-1">Siti / Utente</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {stats.users.total > 0
                ? ((stats.users.premium / stats.users.total) * 100).toFixed(1)
                : "0"}
              %
            </p>
            <p className="text-xs text-gray-500 mt-1">Conversione Premium</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {stats.sites.total > 0
                ? ((stats.sites.published / stats.sites.total) * 100).toFixed(1)
                : "0"}
              %
            </p>
            <p className="text-xs text-gray-500 mt-1">Tasso Pubblicazione</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {stats.users.total > 0
                ? (stats.generations_total / stats.users.total).toFixed(1)
                : "0"}
            </p>
            <p className="text-xs text-gray-500 mt-1">Gen. / Utente</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// TAB: USERS
// ---------------------------------------------------------------------------

function UsersTab() {
  const [data, setData] = useState<PaginatedUsers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const [searchInput, setSearchInput] = useState("");

  // Expanded user detail / edit
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [editUser, setEditUser] = useState<UserRecord | null>(null);
  const [editPlan, setEditPlan] = useState("");
  const [editPremium, setEditPremium] = useState(false);
  const [editActive, setEditActive] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userDetail, setUserDetail] = useState<UserRecord | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Delete
  const [deleteTarget, setDeleteTarget] = useState<UserRecord | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ page: String(page), per_page: "30" });
      if (search) params.set("search", search);
      if (planFilter) params.set("plan", planFilter);
      const d = await adminFetch(`/api/admin/users?${params}`);
      setData(d);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, search, planFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  const toggleExpand = async (user: UserRecord) => {
    if (expandedId === user.id) {
      setExpandedId(null);
      setEditUser(null);
      setUserDetail(null);
      return;
    }
    setExpandedId(user.id);
    setEditUser(user);
    setEditPlan(user.plan);
    setEditPremium(user.is_premium);
    setEditActive(user.is_active);
    setLoadingDetail(true);
    try {
      const detail = await adminFetch(`/api/admin/users/${user.id}`);
      setUserDetail(detail);
    } catch {
      setUserDetail(null);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSaveUser = async () => {
    if (!editUser) return;
    setSaving(true);
    try {
      await adminFetch(`/api/admin/users/${editUser.id}`, {
        method: "PUT",
        body: JSON.stringify({
          plan: editPlan,
          is_premium: editPremium,
          is_active: editActive,
        }),
      });
      setExpandedId(null);
      setEditUser(null);
      load();
    } catch (err: any) {
      alert("Errore salvataggio: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await adminFetch(`/api/admin/users/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      if (expandedId === deleteTarget.id) {
        setExpandedId(null);
        setEditUser(null);
      }
      load();
    } catch (err: any) {
      alert("Errore eliminazione: " + err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Cerca per email o nome..."
            className="flex-1 px-3 py-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm hover:bg-indigo-700 transition-colors"
          >
            Cerca
          </button>
        </form>
        <select
          value={planFilter}
          onChange={(e) => {
            setPlanFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
        >
          <option value="">Tutti i piani</option>
          <option value="free">Free</option>
          <option value="base">Base</option>
          <option value="premium">Premium</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={load} className="text-sm text-indigo-400 hover:underline">
            Riprova
          </button>
        </div>
      ) : !data || data.users.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">Nessun utente trovato</p>
        </Card>
      ) : (
        <>
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#2a2a2a] text-left">
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Nome</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Piano</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Premium</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Siti</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Registrato</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Azioni</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a2a2a]">
                  {data.users.map((u) => (
                    <Fragment key={u.id}>
                      <tr
                        className={classNames(
                          "hover:bg-[#222] transition-colors cursor-pointer",
                          expandedId === u.id && "bg-[#222]"
                        )}
                        onClick={() => toggleExpand(u)}
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {!u.is_active && (
                              <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" title="Disattivato" />
                            )}
                            <span className="text-white truncate max-w-[200px]">{u.email}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-400 hidden md:table-cell">{u.full_name || "---"}</td>
                        <td className="px-4 py-3">
                          <PlanBadge plan={u.plan} />
                        </td>
                        <td className="px-4 py-3 hidden sm:table-cell">
                          <BoolBadge value={u.is_premium} />
                        </td>
                        <td className="px-4 py-3 text-gray-400 hidden lg:table-cell">{u.sites_count}</td>
                        <td className="px-4 py-3 text-gray-500 text-xs hidden lg:table-cell">{formatDate(u.created_at)}</td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setDeleteTarget(u);
                            }}
                            className="text-gray-600 hover:text-red-400 transition-colors p-1"
                            title="Elimina utente"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                            </svg>
                          </button>
                        </td>
                      </tr>

                      {/* Expanded detail / edit row */}
                      {expandedId === u.id && (
                        <tr>
                          <td colSpan={7} className="bg-[#151515] px-4 py-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              {/* Left: user info */}
                              <div className="space-y-3">
                                <h4 className="text-sm font-semibold text-white">Dettagli Utente</h4>
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                  <div>
                                    <span className="text-gray-500">ID:</span>{" "}
                                    <span className="text-gray-300">{u.id}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Email:</span>{" "}
                                    <span className="text-gray-300">{u.email}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Generazioni:</span>{" "}
                                    <span className="text-gray-300">{u.generations_used}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Ultimo login:</span>{" "}
                                    <span className="text-gray-300">{timeAgo(u.last_login)}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Registrato:</span>{" "}
                                    <span className="text-gray-300">{formatDateTime(u.created_at)}</span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Attivo:</span>{" "}
                                    <BoolBadge value={u.is_active} />
                                  </div>
                                </div>
                                {/* User sites */}
                                {loadingDetail ? (
                                  <div className="flex items-center gap-2 text-xs text-gray-500">
                                    <Spinner size="sm" /> Caricamento siti...
                                  </div>
                                ) : userDetail?.sites && userDetail.sites.length > 0 ? (
                                  <div>
                                    <p className="text-xs text-gray-500 mb-1">
                                      Siti ({userDetail.sites.length}):
                                    </p>
                                    <div className="space-y-1">
                                      {userDetail.sites.map((s) => (
                                        <div
                                          key={s.id}
                                          className="flex items-center gap-2 text-xs bg-[#1a1a1a] rounded px-2 py-1"
                                        >
                                          <StatusBadge status={s.status} />
                                          <span className="text-gray-300 truncate">{s.name}</span>
                                          {s.is_published && (
                                            <span className="text-blue-400 text-[10px]">LIVE</span>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                ) : (
                                  <p className="text-xs text-gray-600">Nessun sito creato</p>
                                )}
                              </div>

                              {/* Right: edit form */}
                              <div className="space-y-3">
                                <h4 className="text-sm font-semibold text-white">Modifica Utente</h4>
                                <div>
                                  <label className="block text-xs text-gray-500 mb-1">Piano</label>
                                  <select
                                    value={editPlan}
                                    onChange={(e) => setEditPlan(e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg bg-[#0a0a0a] border border-[#2a2a2a] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                                  >
                                    <option value="free">Free</option>
                                    <option value="base">Base</option>
                                    <option value="premium">Premium</option>
                                  </select>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-xs text-gray-400">Premium</span>
                                  <button
                                    onClick={() => setEditPremium(!editPremium)}
                                    className={classNames(
                                      "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                      editPremium ? "bg-indigo-600" : "bg-[#2a2a2a]"
                                    )}
                                  >
                                    <span
                                      className={classNames(
                                        "inline-block h-4 w-4 rounded-full bg-white transition-transform",
                                        editPremium ? "translate-x-6" : "translate-x-1"
                                      )}
                                    />
                                  </button>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-xs text-gray-400">Attivo</span>
                                  <button
                                    onClick={() => setEditActive(!editActive)}
                                    className={classNames(
                                      "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                      editActive ? "bg-green-600" : "bg-[#2a2a2a]"
                                    )}
                                  >
                                    <span
                                      className={classNames(
                                        "inline-block h-4 w-4 rounded-full bg-white transition-transform",
                                        editActive ? "translate-x-6" : "translate-x-1"
                                      )}
                                    />
                                  </button>
                                </div>
                                <div className="flex gap-2 pt-2">
                                  <button
                                    onClick={handleSaveUser}
                                    disabled={saving}
                                    className="flex-1 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                  >
                                    {saving && <Spinner size="sm" />}
                                    Salva
                                  </button>
                                  <button
                                    onClick={() => {
                                      setExpandedId(null);
                                      setEditUser(null);
                                    }}
                                    className="px-4 py-2 rounded-lg bg-[#2a2a2a] text-gray-300 text-sm hover:bg-[#333] transition-colors"
                                  >
                                    Chiudi
                                  </button>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-600">
              {data.total} utenti totali &middot; Pagina {data.page} di {data.pages}
            </p>
            <Pagination page={data.page} pages={data.pages} onPage={setPage} />
          </div>
        </>
      )}

      {/* Delete confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        title="Elimina Utente"
        message={`Sei sicuro di voler eliminare l'utente "${deleteTarget?.email}"? Questa azione non puo essere annullata. Tutti i siti associati verranno rimossi.`}
        onConfirm={handleDeleteUser}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// TAB: SITES
// ---------------------------------------------------------------------------

function SitesTab() {
  const [data, setData] = useState<PaginatedSites | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [searchInput, setSearchInput] = useState("");

  // Preview modal
  const [previewSite, setPreviewSite] = useState<SiteRecord | null>(null);
  const [previewHtml, setPreviewHtml] = useState("");
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Delete
  const [deleteTarget, setDeleteTarget] = useState<SiteRecord | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ page: String(page), per_page: "30" });
      if (search) params.set("search", search);
      if (statusFilter) params.set("status", statusFilter);
      const d = await adminFetch(`/api/admin/sites?${params}`);
      setData(d);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  const openPreview = async (site: SiteRecord) => {
    setPreviewSite(site);
    setLoadingPreview(true);
    setPreviewHtml("");
    try {
      const detail = await adminFetch(`/api/admin/sites/${site.id}`);
      setPreviewHtml(detail.html_content || "<p style='color:#999;text-align:center;padding:2rem;'>Nessun contenuto HTML disponibile</p>");
    } catch {
      setPreviewHtml("<p style='color:red;text-align:center;padding:2rem;'>Errore nel caricamento</p>");
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleDeleteSite = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await adminFetch(`/api/admin/sites/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      load();
    } catch (err: any) {
      alert("Errore eliminazione: " + err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Cerca siti per nome o proprietario..."
            className="flex-1 px-3 py-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] text-white text-sm placeholder-gray-600 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm hover:bg-indigo-700 transition-colors"
          >
            Cerca
          </button>
        </form>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
        >
          <option value="">Tutti gli stati</option>
          <option value="ready">Pronti</option>
          <option value="generating">In generazione</option>
          <option value="published">Pubblicati</option>
          <option value="draft">Bozza</option>
          <option value="error">Errore</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={load} className="text-sm text-indigo-400 hover:underline">
            Riprova
          </button>
        </div>
      ) : !data || data.sites.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">Nessun sito trovato</p>
        </Card>
      ) : (
        <>
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#2a2a2a] text-left">
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Proprietario</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Stato</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Pubblicato</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Template</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Creato</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">Azioni</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a2a2a]">
                  {data.sites.map((s) => (
                    <tr key={s.id} className="hover:bg-[#222] transition-colors">
                      <td className="px-4 py-3">
                        <span className="text-white truncate block max-w-[200px]">{s.name}</span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs hidden md:table-cell">
                        {s.owner_email || s.owner_name || `ID ${s.user_id}`}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={s.status} />
                      </td>
                      <td className="px-4 py-3 hidden sm:table-cell">
                        <BoolBadge value={s.is_published} />
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs hidden lg:table-cell">
                        {s.template_category
                          ? `${s.template_category}${s.template_style ? ` / ${s.template_style}` : ""}`
                          : "---"}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs hidden lg:table-cell">{formatDate(s.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => openPreview(s)}
                            className="text-gray-600 hover:text-indigo-400 transition-colors p-1"
                            title="Anteprima HTML"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                          </button>
                          {s.published_url && (
                            <a
                              href={s.published_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-gray-600 hover:text-blue-400 transition-colors p-1"
                              title="Apri sito pubblicato"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                              </svg>
                            </a>
                          )}
                          <button
                            onClick={() => setDeleteTarget(s)}
                            className="text-gray-600 hover:text-red-400 transition-colors p-1"
                            title="Elimina sito"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-600">
              {data.total} siti totali &middot; Pagina {data.page} di {data.pages}
            </p>
            <Pagination page={data.page} pages={data.pages} onPage={setPage} />
          </div>
        </>
      )}

      {/* HTML Preview Modal */}
      {previewSite && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl w-[95vw] h-[90vh] max-w-6xl flex flex-col shadow-2xl">
            {/* Modal header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-[#2a2a2a] flex-shrink-0">
              <div className="flex items-center gap-3">
                <h3 className="text-sm font-semibold text-white truncate max-w-[300px]">
                  {previewSite.name}
                </h3>
                <StatusBadge status={previewSite.status} />
              </div>
              <button
                onClick={() => {
                  setPreviewSite(null);
                  setPreviewHtml("");
                }}
                className="text-gray-500 hover:text-white transition-colors p-1"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {/* Modal body */}
            <div className="flex-1 overflow-hidden">
              {loadingPreview ? (
                <div className="flex items-center justify-center h-full">
                  <Spinner size="lg" />
                </div>
              ) : (
                <iframe
                  srcDoc={previewHtml}
                  className="w-full h-full border-0"
                  sandbox="allow-scripts allow-same-origin"
                  title="Anteprima sito"
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        title="Elimina Sito"
        message={`Sei sicuro di voler eliminare il sito "${deleteTarget?.name}"? Questa azione non puo essere annullata.`}
        onConfirm={handleDeleteSite}
        onCancel={() => setDeleteTarget(null)}
        loading={deleting}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// TAB: SETTINGS
// ---------------------------------------------------------------------------

function SettingsTab() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminFetch("/api/admin/stats")
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  const planConfigs = [
    {
      name: "Free",
      features: ["1 sito", "Template base", "3 generazioni AI", "Sottodominio incluso"],
      color: "border-gray-700",
    },
    {
      name: "Base",
      features: [
        "5 siti",
        "Tutti i template",
        "20 generazioni AI",
        "Dominio personalizzato",
        "Rimozione watermark",
      ],
      color: "border-blue-800",
    },
    {
      name: "Premium",
      features: [
        "Siti illimitati",
        "Tutti i template + priority",
        "Generazioni illimitate",
        "Dominio personalizzato",
        "Supporto prioritario",
        "API access",
      ],
      color: "border-purple-800",
    },
  ];

  return (
    <div className="space-y-6">
      {/* System Info */}
      <Card className="p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Informazioni Sistema</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { label: "API URL", value: API_URL },
            { label: "Versione", value: "1.0.0" },
            { label: "Frontend", value: "Next.js 14 + React 18" },
            { label: "Backend", value: "FastAPI (Python)" },
            { label: "Database", value: "PostgreSQL" },
            { label: "Hosting", value: "Render.com" },
          ].map((item) => (
            <div key={item.label} className="bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a]">
              <p className="text-xs text-gray-500 mb-0.5">{item.label}</p>
              <p className="text-sm text-gray-300 break-all">{item.value}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Database stats summary */}
      {stats && (
        <Card className="p-5">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Riepilogo Database</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a] text-center">
              <p className="text-2xl font-bold text-white">{stats.users.total}</p>
              <p className="text-xs text-gray-500 mt-1">Utenti</p>
            </div>
            <div className="bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a] text-center">
              <p className="text-2xl font-bold text-white">{stats.sites.total}</p>
              <p className="text-xs text-gray-500 mt-1">Siti</p>
            </div>
            <div className="bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a] text-center">
              <p className="text-2xl font-bold text-white">{stats.generations_total}</p>
              <p className="text-xs text-gray-500 mt-1">Generazioni</p>
            </div>
            <div className="bg-[#0a0a0a] rounded-lg p-3 border border-[#2a2a2a] text-center">
              <p className="text-2xl font-bold text-white">{stats.users.active}</p>
              <p className="text-xs text-gray-500 mt-1">Utenti Attivi</p>
            </div>
          </div>
        </Card>
      )}

      {/* Plan configs */}
      <Card className="p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Configurazione Piani</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {planConfigs.map((plan) => (
            <div
              key={plan.name}
              className={classNames(
                "bg-[#0a0a0a] rounded-lg p-4 border",
                plan.color
              )}
            >
              <h4 className="text-sm font-semibold text-white mb-3">{plan.name}</h4>
              <ul className="space-y-1.5">
                {plan.features.map((f, i) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-gray-400">
                    <svg className="w-3.5 h-3.5 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              {stats && (
                <div className="mt-3 pt-3 border-t border-[#2a2a2a]">
                  <p className="text-xs text-gray-500">
                    Utenti:{" "}
                    <span className="text-white font-medium">
                      {plan.name === "Free"
                        ? stats.plans.free
                        : plan.name === "Base"
                        ? stats.plans.base
                        : stats.plans.premium}
                    </span>
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Admin session */}
      <Card className="p-5">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Sessione Admin</h3>
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            <p>Token salvato in sessionStorage</p>
            <p className="mt-1">La sessione scade alla chiusura del browser</p>
          </div>
          <button
            onClick={() => {
              sessionStorage.removeItem("admin_token");
              window.location.reload();
            }}
            className="px-4 py-2 rounded-lg bg-red-900/30 border border-red-900/50 text-red-400 text-sm hover:bg-red-900/50 transition-colors"
          >
            Logout
          </button>
        </div>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MAIN DASHBOARD LAYOUT
// ---------------------------------------------------------------------------

type TabKey = "overview" | "users" | "sites" | "settings";

const TABS: { key: TabKey; label: string; icon: JSX.Element }[] = [
  {
    key: "overview",
    label: "Panoramica",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
      </svg>
    ),
  },
  {
    key: "users",
    label: "Utenti",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
      </svg>
    ),
  },
  {
    key: "sites",
    label: "Siti",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
      </svg>
    ),
  },
  {
    key: "settings",
    label: "Impostazioni",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
];

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Top bar */}
      <header className="sticky top-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-[#2a2a2a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            {/* Left: logo + tabs (desktop) */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
                    />
                  </svg>
                </div>
                <span className="text-sm font-semibold text-white hidden sm:inline">E-quipe Admin</span>
              </div>

              {/* Desktop tabs */}
              <nav className="hidden md:flex items-center gap-1">
                {TABS.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={classNames(
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors",
                      activeTab === tab.key
                        ? "bg-indigo-600/20 text-indigo-400"
                        : "text-gray-500 hover:text-gray-300 hover:bg-[#1a1a1a]"
                    )}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            {/* Right: actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  // Force reload of current tab data
                  const current = activeTab;
                  setActiveTab("settings");
                  setTimeout(() => setActiveTab(current), 0);
                }}
                className="text-gray-600 hover:text-gray-300 transition-colors p-2"
                title="Ricarica dati"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
                </svg>
              </button>
              <button
                onClick={onLogout}
                className="text-gray-600 hover:text-red-400 transition-colors p-2"
                title="Logout"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                </svg>
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden text-gray-500 hover:text-white transition-colors p-2"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile tabs */}
          {mobileMenuOpen && (
            <nav className="md:hidden pb-3 flex flex-col gap-1">
              {TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => {
                    setActiveTab(tab.key);
                    setMobileMenuOpen(false);
                  }}
                  className={classNames(
                    "flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors text-left",
                    activeTab === tab.key
                      ? "bg-indigo-600/20 text-indigo-400"
                      : "text-gray-500 hover:text-gray-300 hover:bg-[#1a1a1a]"
                  )}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </nav>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {activeTab === "overview" && <OverviewTab />}
        {activeTab === "users" && <UsersTab />}
        {activeTab === "sites" && <SitesTab />}
        {activeTab === "settings" && <SettingsTab />}
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ROOT PAGE COMPONENT
// ---------------------------------------------------------------------------

export default function AdminPage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // Check if we already have a valid token
    const token = sessionStorage.getItem("admin_token");
    if (token) {
      // Quick verify by hitting stats endpoint
      adminFetch("/api/admin/stats")
        .then(() => setAuthenticated(true))
        .catch(() => {
          sessionStorage.removeItem("admin_token");
          setAuthenticated(false);
        })
        .finally(() => setChecking(false));
    } else {
      setChecking(false);
    }
  }, []);

  const handleLogout = () => {
    sessionStorage.removeItem("admin_token");
    setAuthenticated(false);
  };

  if (checking) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!authenticated) {
    return <LoginScreen onLogin={() => setAuthenticated(true)} />;
  }

  return <Dashboard onLogout={handleLogout} />;
}
