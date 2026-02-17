"use client";

import { useState, useEffect, useMemo } from "react";
import { API_BASE } from "@/lib/api";
import {
  BookOpen,
  Search,
  ChevronRight,
  Target,
  FileText,
  Code,
  ExternalLink,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  Wrench,
  X,
  CheckCircle,
  Shield,
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
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  });
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  lastUpdated: string;
}

interface BenchmarkRow {
  sector: string;
  googleCpc: { min: number; max: number };
  metaCpc: { min: number; max: number };
  cplRange: { min: number; max: number };
  recommendedBudget: number;
  platformSplit: { google: number; meta: number };
}

interface ProblemItem {
  symptom: string;
  diagnosis: string;
  solution: string[];
}

interface VerticalTemplate {
  id: string;
  name: string;
  icon: string;
  budget: { min: number; recommended: number; split: { google: number; meta: number } };
  keywords: { main: string[]; negative: string[] };
  targeting: {
    ageMin: number;
    ageMax: number;
    radiusKm: number;
    interests: string[];
  };
  adCopy: { googleHeadlines: string[]; metaHooks: string[] };
  kpi: { ctr: number; cpc: number; cpl: number; conversionRate: number };
}

interface CategoryDef {
  id: string;
  name: string;
  description: string;
  icon: typeof FileText;
}

const categoryDefs: CategoryDef[] = [
  { id: "google", name: "Google Ads", description: "Guida completa operativa Google Ads", icon: FileText },
  { id: "meta", name: "Meta Ads", description: "Guida completa operativa Meta Ads", icon: FileText },
  { id: "meta-ads", name: "Meta Ads Avanzato", description: "Manuale operativo completo Meta/Instagram Ads con benchmark", icon: FileText },
  { id: "strategy", name: "Strategie", description: "Strategie per settore e confronto piattaforme", icon: Target },
  { id: "technical", name: "Tecniche", description: "Tracking, policy, dimensioni creative", icon: Code },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function KnowledgePage() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkRow[]>([]);
  const [problems, setProblems] = useState<ProblemItem[]>([]);
  const [verticals, setVerticals] = useState<VerticalTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<KnowledgeArticle | null>(null);
  const [selectedVertical, setSelectedVertical] = useState<VerticalTemplate | null>(null);
  const [showBenchmarks, setShowBenchmarks] = useState(false);
  const [showProblemSolving, setShowProblemSolving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await adminFetch("/api/ads/knowledge");
        setArticles(data.articles || []);
        setBenchmarks(data.benchmarks || []);
        setProblems(data.problems || []);
        setVerticals(data.verticals || []);
      } catch {
        // API not yet available -- use empty
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const totalArticles = articles.length;

  const filteredArticles = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return articles.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.content.toLowerCase().includes(q) ||
        a.tags.some((t) => t.toLowerCase().includes(q))
    );
  }, [searchQuery, articles]);

  const categoryArticles = useMemo(() => {
    if (!selectedCategory) return [];
    return articles.filter((a) => a.category === selectedCategory);
  }, [selectedCategory, articles]);

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
          <h1 className="text-2xl font-bold text-white">Knowledge Base</h1>
          <p className="text-gray-500">Manuale Operativo Ads — Aggiornato Febbraio 2026</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
          <BookOpen className="w-5 h-5 text-amber-400" />
          <span className="text-amber-400 font-medium text-sm">{totalArticles} articoli</span>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
        <input
          type="text"
          placeholder='Cerca nella knowledge base... (es: "keyword negative", "consent mode")'
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-lg bg-[#141420] border border-white/10 text-white placeholder-gray-500 focus:border-amber-500/50 focus:outline-none text-sm"
        />
      </div>

      {/* Search Results */}
      {searchQuery.trim() && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Risultati ricerca ({filteredArticles.length})
            </h2>
            <button
              onClick={() => setSearchQuery("")}
              className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
            >
              <X className="w-4 h-4" /> Cancella
            </button>
          </div>

          {filteredArticles.length === 0 ? (
            <div className="rounded-xl bg-[#141420] border border-white/5 p-8 text-center">
              <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">
                Nessun risultato trovato per &quot;{searchQuery}&quot;
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredArticles.map((article) => (
                <button
                  key={article.id}
                  onClick={() => setSelectedArticle(article)}
                  className="w-full text-left rounded-xl bg-[#141420] border border-white/5 p-4 hover:border-amber-500/30 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-medium text-white">{article.title}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {article.content.substring(0, 150)}...
                      </p>
                      <div className="flex gap-2 mt-2">
                        {article.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-600 shrink-0" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main content (no search) */}
      {!searchQuery.trim() && (
        <>
          {/* Categories */}
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">Categorie</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {categoryDefs.map((cat) => {
                const Icon = cat.icon;
                const count = articles.filter((a) => a.category === cat.id).length;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-amber-500/30 transition-colors group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                        <Icon className="w-6 h-6 text-amber-400" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white group-hover:text-amber-400 transition-colors mb-1">
                          {cat.name}
                        </h3>
                        <p className="text-sm text-gray-500 mb-2">{cat.description}</p>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400">
                          {count} articoli
                        </span>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-amber-400 group-hover:translate-x-1 transition-all shrink-0" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Category articles */}
          {selectedCategory && (
            <div className="rounded-xl bg-[#141420] border border-amber-500/30 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white text-lg">
                  {categoryDefs.find((c) => c.id === selectedCategory)?.name}
                </h3>
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="p-1 rounded-lg hover:bg-white/5 text-gray-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-3">
                {categoryArticles.map((article) => (
                  <button
                    key={article.id}
                    onClick={() => setSelectedArticle(article)}
                    className="w-full text-left p-4 rounded-lg bg-[#1a1a2e]/50 hover:bg-[#1a1a2e] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-white">{article.title}</h4>
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    </div>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-1">
                      {article.content.substring(0, 100)}...
                    </p>
                  </button>
                ))}
                {categoryArticles.length === 0 && (
                  <p className="text-gray-500 text-sm">
                    Nessun articolo in questa categoria. I dati verranno caricati dal backend.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Quick Tools */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setShowBenchmarks(!showBenchmarks)}
              className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-emerald-500/30 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Benchmark Italia</h3>
                  <p className="text-sm text-gray-500">CPC, CPL, CTR per settore</p>
                </div>
              </div>
            </button>

            <button
              onClick={() => setShowProblemSolving(!showProblemSolving)}
              className="rounded-xl bg-[#141420] border border-white/5 p-6 text-left hover:border-amber-500/30 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                  <Wrench className="w-6 h-6 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Problem Solving</h3>
                  <p className="text-sm text-gray-500">Diagnosi e soluzioni rapide</p>
                </div>
              </div>
            </button>

            <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <Lightbulb className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Best Practice 2026</h3>
                  <p className="text-sm text-gray-500">Consigli aggiornati</p>
                </div>
              </div>
            </div>
          </div>

          {/* Benchmarks Panel */}
          {showBenchmarks && benchmarks.length > 0 && (
            <div className="rounded-xl bg-[#141420] border border-emerald-500/30 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-emerald-400" />
                  Benchmark per Settore — Italia 2026
                </h3>
                <button
                  onClick={() => setShowBenchmarks(false)}
                  className="p-1 rounded-lg hover:bg-white/5 text-gray-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Settore</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Google CPC</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Meta CPC</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">CPL Range</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Budget Min</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Split G/M</th>
                    </tr>
                  </thead>
                  <tbody>
                    {benchmarks.map((b) => (
                      <tr key={b.sector} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4 text-white font-medium">{b.sector}</td>
                        <td className="py-3 px-4 text-gray-400">€{b.googleCpc.min}-{b.googleCpc.max}</td>
                        <td className="py-3 px-4 text-gray-400">€{b.metaCpc.min}-{b.metaCpc.max}</td>
                        <td className="py-3 px-4 text-gray-400">€{b.cplRange.min}-{b.cplRange.max}</td>
                        <td className="py-3 px-4 text-gray-400">€{b.recommendedBudget}/mese</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">{b.platformSplit.google}%</span>
                            <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded">{b.platformSplit.meta}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Problem Solving Panel */}
          {showProblemSolving && problems.length > 0 && (
            <div className="rounded-xl bg-[#141420] border border-amber-500/30 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-white text-lg flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-amber-400" />
                  Matrice Problem Solving
                </h3>
                <button
                  onClick={() => setShowProblemSolving(false)}
                  className="p-1 rounded-lg hover:bg-white/5 text-gray-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-4">
                {problems.map((p, idx) => (
                  <div key={idx} className="p-4 rounded-lg bg-[#1a1a2e]/50">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-medium text-white">{p.symptom}</h4>
                        <p className="text-sm text-gray-500 mt-1">{p.diagnosis}</p>
                        <div className="mt-3 space-y-1">
                          <p className="text-xs font-medium text-gray-400 uppercase">Soluzione:</p>
                          {p.solution.map((sol, sidx) => (
                            <div key={sidx} className="flex items-center gap-2 text-sm text-gray-300">
                              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                              {sol}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Vertical Templates */}
          {verticals.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">Template per Verticale</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {verticals.map((v) => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedVertical(v)}
                    className="rounded-xl bg-[#141420] border border-white/5 p-4 text-left hover:border-amber-500/30 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{v.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white text-sm group-hover:text-amber-400 transition-colors truncate">
                          {v.name}
                        </p>
                        <p className="text-xs text-gray-500">Budget: €{v.budget.min}/mese</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-amber-400 transition-colors shrink-0" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Vertical Detail */}
          {selectedVertical && (
            <div className="rounded-xl bg-[#141420] border border-amber-500/30 p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-white text-lg flex items-center gap-2">
                  <span className="text-2xl">{selectedVertical.icon}</span>
                  {selectedVertical.name}
                </h3>
                <button
                  onClick={() => setSelectedVertical(null)}
                  className="p-1 rounded-lg hover:bg-white/5 text-gray-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Budget & Platforms */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <p className="text-xs text-gray-500 uppercase">Budget Minimo</p>
                  <p className="text-xl font-bold text-white">€{selectedVertical.budget.min}</p>
                </div>
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <p className="text-xs text-gray-500 uppercase">Budget Consigliato</p>
                  <p className="text-xl font-bold text-emerald-400">€{selectedVertical.budget.recommended}</p>
                </div>
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <p className="text-xs text-gray-500 uppercase">Google</p>
                  <p className="text-xl font-bold text-blue-400">{selectedVertical.budget.split.google}%</p>
                </div>
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <p className="text-xs text-gray-500 uppercase">Meta</p>
                  <p className="text-xl font-bold text-purple-400">{selectedVertical.budget.split.meta}%</p>
                </div>
              </div>

              {/* Keywords */}
              <div>
                <h4 className="font-medium text-white mb-2">Keyword Consigliate</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedVertical.keywords.main.map((kw) => (
                    <span key={kw} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Negative Keywords */}
              <div>
                <h4 className="font-medium text-white mb-2">Keyword Negative</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedVertical.keywords.negative.map((kw) => (
                    <span key={kw} className="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Targeting */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase">Eta</p>
                  <p className="text-white">{selectedVertical.targeting.ageMin}-{selectedVertical.targeting.ageMax}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Raggio</p>
                  <p className="text-white">{selectedVertical.targeting.radiusKm} km</p>
                </div>
                <div className="col-span-2">
                  <p className="text-xs text-gray-500 uppercase">Interessi</p>
                  <p className="text-white">{selectedVertical.targeting.interests.join(", ")}</p>
                </div>
              </div>

              {/* Ad Copy */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <h4 className="font-medium text-white mb-2">Google Headlines</h4>
                  <ul className="space-y-1">
                    {selectedVertical.adCopy.googleHeadlines.map((h, i) => (
                      <li key={i} className="text-sm text-gray-400">- {h}</li>
                    ))}
                  </ul>
                </div>
                <div className="p-4 rounded-lg bg-[#1a1a2e]/50">
                  <h4 className="font-medium text-white mb-2">Meta Hooks</h4>
                  <ul className="space-y-1">
                    {selectedVertical.adCopy.metaHooks.map((h, i) => (
                      <li key={i} className="text-sm text-gray-400">- {h}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* KPI */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-emerald-500/10">
                  <p className="text-xs text-gray-500">CTR Target</p>
                  <p className="text-lg font-bold text-emerald-400">{(selectedVertical.kpi.ctr * 100).toFixed(1)}%</p>
                </div>
                <div className="p-3 rounded-lg bg-blue-500/10">
                  <p className="text-xs text-gray-500">CPC Medio</p>
                  <p className="text-lg font-bold text-blue-400">€{selectedVertical.kpi.cpc}</p>
                </div>
                <div className="p-3 rounded-lg bg-purple-500/10">
                  <p className="text-xs text-gray-500">CPL Target</p>
                  <p className="text-lg font-bold text-purple-400">€{selectedVertical.kpi.cpl}</p>
                </div>
                <div className="p-3 rounded-lg bg-amber-500/10">
                  <p className="text-xs text-gray-500">Conv. Rate</p>
                  <p className="text-lg font-bold text-amber-400">{(selectedVertical.kpi.conversionRate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          )}

          {/* Optimization Rules + External Resources */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
              <h3 className="font-semibold text-white mb-4">Regole di Ottimizzazione</h3>
              <div className="space-y-3">
                {[
                  { rule: "Budget Cap", desc: "Hard limit 120% budget giornaliero" },
                  { rule: "Incremento Graduale", desc: "Max +20% in 24h, +50% in 7 giorni" },
                  { rule: "Circuit Breaker", desc: "Pausa auto se CPA > 200% target" },
                  { rule: "Anomaly Detection", desc: "Flag se CTR cambia > 50% in 24h" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#1a1a2e]/50">
                    <div>
                      <p className="font-medium text-white text-sm">{item.rule}</p>
                      <p className="text-xs text-gray-500">{item.desc}</p>
                    </div>
                    <Shield className="w-4 h-4 text-amber-400" />
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl bg-[#141420] border border-white/5 p-6">
              <h3 className="font-semibold text-white mb-4">Risorse Esterne</h3>
              <div className="space-y-3">
                {[
                  { name: "Google Ads Policy", url: "https://support.google.com/adspolicy" },
                  { name: "Meta Advertising Standards", url: "https://www.facebook.com/policies/ads" },
                  { name: "Google Ads API v22", url: "https://developers.google.com/google-ads/api/docs/start" },
                  { name: "Meta Marketing API", url: "https://developers.facebook.com/docs/marketing-apis" },
                ].map((item, i) => (
                  <a
                    key={i}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-3 rounded-lg bg-[#1a1a2e]/50 hover:bg-[#1a1a2e] transition-colors group"
                  >
                    <span className="text-white text-sm group-hover:text-amber-400 transition-colors">
                      {item.name}
                    </span>
                    <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-amber-400 transition-colors" />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Article Detail Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#141420] rounded-2xl border border-white/10 w-full max-w-3xl max-h-[80vh] overflow-auto">
            <div className="sticky top-0 bg-[#141420] z-10 border-b border-white/10 p-6 flex items-center justify-between">
              <div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 mb-2 inline-block">
                  {categoryDefs.find((c) => c.id === selectedArticle.category)?.name ||
                    selectedArticle.category}
                </span>
                <h2 className="font-bold text-white text-lg">{selectedArticle.title}</h2>
              </div>
              <button
                onClick={() => setSelectedArticle(null)}
                className="p-2 rounded-lg hover:bg-white/5 text-gray-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <div className="prose prose-invert max-w-none text-sm text-gray-400 whitespace-pre-line">
                {selectedArticle.content}
              </div>
              <div className="mt-6 pt-6 border-t border-white/10">
                <p className="text-xs text-gray-500 mb-2">Tags:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedArticle.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-4">
                  Ultimo aggiornamento:{" "}
                  {new Date(selectedArticle.lastUpdated).toLocaleDateString("it-IT")}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
