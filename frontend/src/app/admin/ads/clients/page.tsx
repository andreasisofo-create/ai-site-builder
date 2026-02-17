"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import {
  Plus,
  Search,
  MapPin,
  Filter,
  Play,
  Loader2,
  AlertCircle,
  CheckCircle,
  Globe,
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
// Types
// ---------------------------------------------------------------------------
interface Client {
  id: string;
  name: string;
  businessName: string;
  businessType: string;
  city?: string;
  region?: string;
  website?: string;
  websiteUrl?: string;
  isActive: boolean;
  monthlyBudget?: number;
}

const businessTypes = [
  { id: "all", label: "Tutti" },
  { id: "ristorante", label: "Ristorante / Pizzeria" },
  { id: "ecommerce", label: "E-commerce" },
  { id: "studio_legale", label: "Studio Legale" },
  { id: "commercialista", label: "Commercialista" },
  { id: "palestra", label: "Palestra / Fitness" },
  { id: "immobiliare", label: "Agenzia Immobiliare" },
  { id: "estetica", label: "Centro Estetico" },
  { id: "parrucchiere", label: "Parrucchiere" },
  { id: "edile", label: "Impresa Edile" },
  { id: "fotografo", label: "Fotografo" },
  { id: "creativo", label: "Studio Creativo" },
  { id: "startup", label: "Startup / Tech" },
  { id: "saas", label: "SaaS / Software" },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ClientsPage() {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    business_name: "",
    business_type: "",
    city: "",
    email: "",
    region: "",
    phone: "",
    website_url: "",
    budget_monthly: 0,
  });

  const loadClients = async () => {
    try {
      const data = await adminFetch("/api/ads/clients");
      setClients(data.data || data.clients || []);
    } catch {
      // API not available yet
    }
  };

  useEffect(() => {
    const load = async () => {
      await loadClients();
      setLoading(false);
    };
    load();
  }, []);

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminFetch("/api/ads/clients", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      setShowAddModal(false);
      setFormData({
        business_name: "",
        business_type: "",
        city: "",
        email: "",
        region: "",
        phone: "",
        website_url: "",
        budget_monthly: 0,
      });
      await loadClients();
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  const filtered = clients.filter((c) => {
    const matchSearch =
      (c.businessName || c.name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.city || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchType = filterType === "all" || c.businessType === filterType;
    return matchSearch && matchType;
  });

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
          <h1 className="text-2xl font-bold text-white">Clienti</h1>
          <p className="text-gray-500">Seleziona un cliente per creare campagne pubblicitarie</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nuovo Cliente
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Cerca cliente per nome o citta..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white text-sm focus:border-amber-500/50 focus:outline-none"
          >
            {businessTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="flex gap-4 text-sm text-gray-400">
        <span>
          Totale: <strong className="text-white">{clients.length}</strong> clienti
        </span>
        <span className="text-gray-600">|</span>
        <span>
          Attivi:{" "}
          <strong className="text-emerald-400">
            {clients.filter((c) => c.isActive).length}
          </strong>
        </span>
        <span className="text-gray-600">|</span>
        <span>
          Selezionato:{" "}
          {selectedId ? (
            <strong className="text-amber-400">
              {(clients.find((c) => c.id === selectedId)?.name ||
                clients.find((c) => c.id === selectedId)?.businessName) ??
                "-"}
            </strong>
          ) : (
            <span className="text-gray-500">Nessuno</span>
          )}
        </span>
      </div>

      {/* Empty State */}
      {clients.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-white/10 p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Nessun cliente trovato</h3>
          <p className="text-gray-400 max-w-md mx-auto mb-6">
            Inizia aggiungendo il tuo primo cliente. Ti servira l&apos;URL del sito web per
            permettere all&apos;AI di analizzare il business.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 text-black font-medium text-sm hover:bg-amber-400 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Aggiungi Primo Cliente
          </button>
        </div>
      )}

      {/* Clients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((client) => {
          const isSelected = selectedId === client.id;
          const siteUrl = client.website || client.websiteUrl;

          return (
            <div
              key={client.id}
              onClick={() => setSelectedId(client.id)}
              className={`rounded-xl bg-[#141420] border p-6 cursor-pointer transition-all group ${
                isSelected
                  ? "ring-2 ring-amber-500 border-amber-500"
                  : "border-white/5 hover:border-white/10"
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div
                    className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl font-bold ${
                      isSelected
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-gradient-to-br from-amber-500/20 to-amber-500/10 text-amber-300"
                    }`}
                  >
                    {(client.name || client.businessName || "C").charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">
                      {client.name || client.businessName}
                    </h3>
                    <p className="text-sm text-gray-500 capitalize">
                      {businessTypes.find((t) => t.id === client.businessType)?.label ||
                        client.businessType}
                    </p>
                  </div>
                </div>
                {isSelected && (
                  <div className="w-6 h-6 rounded-full bg-amber-500 flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>

              <div className="space-y-2 mb-4">
                {client.city && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <MapPin className="w-4 h-4" />
                    {client.city}
                    {client.region ? `, ${client.region}` : ", Italia"}
                  </div>
                )}
                {siteUrl ? (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Globe className="w-4 h-4" />
                    <a
                      href={siteUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-amber-400 transition-colors truncate max-w-[200px]"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {siteUrl.replace(/^https?:\/\//, "")}
                    </a>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-sm text-amber-400">
                    <AlertCircle className="w-4 h-4" />
                    Sito web mancante
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    client.isActive
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "bg-white/5 text-gray-500"
                  }`}
                >
                  {client.isActive ? "Attivo" : "Inattivo"}
                </span>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Budget/mese</p>
                  <p className="font-medium text-white text-sm">
                    €{client.monthlyBudget || 0}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-white/5 flex gap-2">
                <button
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isSelected
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "bg-white/5 text-gray-400 hover:bg-white/10"
                  }`}
                >
                  {isSelected ? "Selezionato" : "Seleziona"}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedId(client.id);
                    router.push("/admin/ads/ai-modules");
                  }}
                  className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg bg-amber-500 text-black text-sm font-medium hover:bg-amber-400 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Avvia AI
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Client Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setShowAddModal(false)}
          />
          <div className="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-[#141420] border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Nuovo Cliente</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateClient} className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">
                  Nome Azienda <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.business_name}
                  onChange={(e) =>
                    setFormData((p) => ({ ...p, business_name: e.target.value }))
                  }
                  placeholder="Es: Pizzeria da Mario"
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">
                  Tipo Business <span className="text-red-400">*</span>
                </label>
                <select
                  required
                  value={formData.business_type}
                  onChange={(e) =>
                    setFormData((p) => ({ ...p, business_type: e.target.value }))
                  }
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white text-sm focus:border-amber-500/50 focus:outline-none"
                >
                  <option value="" disabled>
                    Seleziona tipo...
                  </option>
                  {businessTypes
                    .filter((t) => t.id !== "all")
                    .map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.label}
                      </option>
                    ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400 mb-1.5 block">
                    Citta <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.city}
                    onChange={(e) =>
                      setFormData((p) => ({ ...p, city: e.target.value }))
                    }
                    placeholder="Es: Milano"
                    className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-1.5 block">Regione</label>
                  <input
                    type="text"
                    value={formData.region}
                    onChange={(e) =>
                      setFormData((p) => ({ ...p, region: e.target.value }))
                    }
                    placeholder="Es: Lombardia"
                    className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">
                  Email <span className="text-red-400">*</span>
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) =>
                    setFormData((p) => ({ ...p, email: e.target.value }))
                  }
                  placeholder="info@azienda.it"
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">Telefono</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData((p) => ({ ...p, phone: e.target.value }))
                  }
                  placeholder="+39 02 1234567"
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">URL Sito Web</label>
                <input
                  type="url"
                  value={formData.website_url}
                  onChange={(e) =>
                    setFormData((p) => ({ ...p, website_url: e.target.value }))
                  }
                  placeholder="https://www.esempio.it"
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1.5 block">
                  Budget Mensile (EUR)
                </label>
                <input
                  type="number"
                  min={0}
                  value={formData.budget_monthly || ""}
                  onChange={(e) =>
                    setFormData((p) => ({
                      ...p,
                      budget_monthly: parseInt(e.target.value) || 0,
                    }))
                  }
                  placeholder="0"
                  className="w-full py-2.5 px-4 rounded-lg bg-[#0a0a0f] border border-white/10 text-white placeholder-gray-600 focus:border-amber-500/50 focus:outline-none text-sm"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 rounded-lg border border-white/10 text-white text-sm font-medium hover:bg-white/5 transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg bg-amber-500 text-black text-sm font-medium hover:bg-amber-400 transition-colors disabled:opacity-50"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4" />
                  )}
                  {saving ? "Salvataggio..." : "Salva Cliente"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
