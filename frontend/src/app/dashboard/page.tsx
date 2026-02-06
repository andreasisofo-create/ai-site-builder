"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  PlusIcon,
  MagnifyingGlassIcon,
  BellIcon,
  Cog6ToothIcon,
  ArrowRightIcon,
  SparklesIcon,
  RocketLaunchIcon,
  GlobeAltIcon,
  PencilIcon,
  TrashIcon,
  MoreVerticalIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon,
  TemplateIcon,
  PhotoIcon,
  DocumentDuplicateIcon,
  ArrowUpRightIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface Site {
  id: number;
  name: string;
  slug: string;
  description?: string;
  thumbnail?: string;
  is_published: boolean;
  status: "draft" | "generating" | "ready" | "published";
  last_edited: string;
  created_at: string;
}

// Mock data per visualizzazione
const MOCK_SITES: Site[] = [
  {
    id: 1,
    name: "Ristorante Da Mario",
    slug: "ristorante-da-mario",
    description: "Sito web per ristorante italiano tradizionale",
    thumbnail: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&h=400&fit=crop",
    is_published: true,
    status: "published",
    last_edited: "2024-01-15T10:30:00",
    created_at: "2024-01-10T08:00:00",
  },
  {
    id: 2,
    name: "Studio Legale Rossi",
    slug: "studio-legale-rossi",
    description: "Studio legale specializzato in diritto commerciale",
    thumbnail: "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&h=400&fit=crop",
    is_published: false,
    status: "ready",
    last_edited: "2024-01-14T16:45:00",
    created_at: "2024-01-12T09:30:00",
  },
];

const SIDEBAR_ITEMS = [
  { icon: FolderIcon, label: "Progetti", active: true },
  { icon: TemplateIcon, label: "Templates", active: false },
  { icon: PhotoIcon, label: "Media", active: false },
  { icon: DocumentDuplicateIcon, label: "Pagine", active: false },
  { icon: ClockIcon, label: "Storia", active: false },
];

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [sites, setSites] = useState<Site[]>(MOCK_SITES);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeFilter, setActiveFilter] = useState<"all" | "published" | "draft">("all");

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth");
    }
  }, [status, router]);

  const filteredSites = sites.filter((site) => {
    const matchesSearch = site.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         site.slug.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = activeFilter === "all" || 
                         (activeFilter === "published" && site.is_published) ||
                         (activeFilter === "draft" && !site.is_published);
    return matchesSearch && matchesFilter;
  });

  const createSite = () => {
    router.push("/dashboard/new");
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("it-IT", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "published":
        return <CheckCircleIcon className="w-4 h-4 text-emerald-400" />;
      case "generating":
        return <SparklesIcon className="w-4 h-4 text-amber-400 animate-pulse" />;
      case "ready":
        return <RocketLaunchIcon className="w-4 h-4 text-blue-400" />;
      default:
        return <ExclamationCircleIcon className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "published":
        return "Online";
      case "generating":
        return "Generazione...";
      case "ready":
        return "Pronto";
      default:
        return "Bozza";
    }
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex">
      {/* Sidebar Sinistra */}
      <aside
        className={`fixed left-0 top-0 h-full bg-[#111] border-r border-white/5 transition-all duration-300 z-40 ${
          sidebarOpen ? "w-64" : "w-0 -translate-x-full lg:w-20 lg:translate-x-0"
        }`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            {sidebarOpen && (
              <span className="font-semibold text-lg tracking-tight">E-quipe</span>
            )}
          </Link>
        </div>

        {/* Nav Items */}
        <nav className="p-3 space-y-1">
          {SIDEBAR_ITEMS.map((item) => (
            <button
              key={item.label}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                item.active
                  ? "bg-white/10 text-white"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* Create New Button */}
        {sidebarOpen && (
          <div className="p-4 mt-4">
            <button
              onClick={createSite}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-all"
            >
              <PlusIcon className="w-5 h-5" />
              Nuovo Progetto
            </button>
          </div>
        )}

        {/* Upgrade Card */}
        {sidebarOpen && (
          <div className="absolute bottom-4 left-4 right-4 p-4 rounded-xl bg-gradient-to-br from-violet-600/20 to-blue-600/20 border border-white/10">
            <p className="text-sm font-medium mb-1">Piano Starter</p>
            <p className="text-xs text-slate-400 mb-3">3 progetti rimasti</p>
            <button className="w-full py-2 text-xs font-medium bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              Aggiorna Piano
            </button>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarOpen ? "lg:ml-64" : "lg:ml-20"
        }`}
      >
        {/* Header */}
        <header className="h-16 border-b border-white/5 bg-[#0a0a0a]/80 backdrop-blur-xl sticky top-0 z-30">
          <div className="h-full px-6 flex items-center justify-between">
            {/* Left: Toggle + Breadcrumb */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <Bars3Icon className="w-5 h-5 text-slate-400" />
              </button>
              <div className="hidden sm:flex items-center gap-2 text-sm">
                <span className="text-slate-400">Workspace</span>
                <span className="text-slate-600">/</span>
                <span className="text-white font-medium">Progetti</span>
              </div>
            </div>

            {/* Center: Search */}
            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Cerca progetti..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.07] transition-all"
                />
              </div>
            </div>

            {/* Right: Actions + Profile */}
            <div className="flex items-center gap-3">
              <button className="p-2 hover:bg-white/5 rounded-lg transition-colors relative">
                <BellIcon className="w-5 h-5 text-slate-400" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                <Cog6ToothIcon className="w-5 h-5 text-slate-400" />
              </button>
              <div className="w-px h-6 bg-white/10 mx-1" />
              <button className="flex items-center gap-3 pl-2 pr-3 py-1.5 hover:bg-white/5 rounded-lg transition-colors">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-sm font-medium">
                  {session?.user?.name?.[0] || "U"}
                </div>
                <ChevronDownIcon className="w-4 h-4 text-slate-400 hidden sm:block" />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-6">
          {/* Page Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">Progetti</h1>
              <p className="text-slate-400 text-sm mt-1">
                Gestisci i tuoi siti web e le pagine generate
              </p>
            </div>
            <button
              onClick={createSite}
              className="flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-all shadow-lg shadow-blue-600/20"
            >
              <PlusIcon className="w-5 h-5" />
              Crea Nuovo Sito
            </button>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2 mb-6">
            {[
              { key: "all", label: "Tutti", count: sites.length },
              { key: "published", label: "Online", count: sites.filter((s) => s.is_published).length },
              { key: "draft", label: "Bozze", count: sites.filter((s) => !s.is_published).length },
            ].map((filter) => (
              <button
                key={filter.key}
                onClick={() => setActiveFilter(filter.key as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === filter.key
                    ? "bg-white/10 text-white"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {filter.label}
                <span className="ml-2 text-xs text-slate-500">{filter.count}</span>
              </button>
            ))}
          </div>

          {/* Projects Grid */}
          {filteredSites.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-20 h-20 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
                <FolderIcon className="w-10 h-10 text-slate-500" />
              </div>
              <h3 className="text-lg font-medium mb-2">Nessun progetto trovato</h3>
              <p className="text-slate-400 text-sm max-w-sm mb-6">
                Inizia creando il tuo primo sito web professionale con l&apos;AI
              </p>
              <button
                onClick={createSite}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-all"
              >
                <PlusIcon className="w-5 h-5" />
                Crea Progetto
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {/* Create New Card */}
              <button
                onClick={createSite}
                className="group relative aspect-[4/3] rounded-xl border-2 border-dashed border-white/10 hover:border-blue-500/50 bg-white/[0.02] hover:bg-white/[0.04] transition-all flex flex-col items-center justify-center gap-4"
              >
                <div className="w-14 h-14 rounded-full bg-white/5 group-hover:bg-blue-500/20 flex items-center justify-center transition-all">
                  <PlusIcon className="w-7 h-7 text-slate-400 group-hover:text-blue-400 transition-colors" />
                </div>
                <div className="text-center">
                  <p className="font-medium text-slate-300 group-hover:text-white transition-colors">
                    Crea Nuovo Sito
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    Generato con AI in 60 secondi
                  </p>
                </div>
              </button>

              {/* Site Cards */}
              {filteredSites.map((site) => (
                <div
                  key={site.id}
                  className="group relative bg-[#111] rounded-xl border border-white/5 overflow-hidden hover:border-white/10 transition-all hover:shadow-2xl hover:shadow-black/50"
                  onClick={() => setSelectedSite(site)}
                >
                  {/* Thumbnail */}
                  <div className="aspect-[16/10] relative overflow-hidden bg-[#1a1a1a]">
                    {site.thumbnail ? (
                      <Image
                        src={site.thumbnail}
                        alt={site.name}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <GlobeAltIcon className="w-12 h-12 text-slate-600" />
                      </div>
                    )}
                    {/* Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#111] via-transparent to-transparent opacity-60" />
                    
                    {/* Status Badge */}
                    <div className="absolute top-3 left-3 flex items-center gap-2 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm border border-white/10">
                      {getStatusIcon(site.status)}
                      <span className="text-xs font-medium">{getStatusLabel(site.status)}</span>
                    </div>

                    {/* Actions */}
                    <div className="absolute top-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-2 bg-black/60 backdrop-blur-sm rounded-lg hover:bg-black/80 transition-colors">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button className="p-2 bg-black/60 backdrop-blur-sm rounded-lg hover:bg-red-500/80 transition-colors">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <h3 className="font-medium text-white truncate">{site.name}</h3>
                        <p className="text-sm text-slate-400 truncate">{site.slug}.e-quipe.app</p>
                      </div>
                      <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors flex-shrink-0">
                        <MoreVerticalIcon className="w-4 h-4 text-slate-400" />
                      </button>
                    </div>
                    
                    <div className="flex items-center gap-3 mt-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <ClockIcon className="w-3.5 h-3.5" />
                        {formatDate(site.last_edited)}
                      </span>
                      {site.is_published && (
                        <Link
                          href={`https://${site.slug}.e-quipe.app`}
                          target="_blank"
                          className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ArrowUpRightIcon className="w-3.5 h-3.5" />
                          Visita
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Inspector Sidebar (Right) - Mostrato quando un progetto è selezionato */}
      {selectedSite && (
        <aside className="fixed right-0 top-0 h-full w-80 bg-[#111] border-l border-white/5 z-40 overflow-y-auto">
          <div className="p-4 border-b border-white/5 flex items-center justify-between">
            <h3 className="font-medium">Dettagli Progetto</h3>
            <button
              onClick={() => setSelectedSite(null)}
              className="p-1.5 hover:bg-white/5 rounded-lg transition-colors"
            >
              <XMarkIcon className="w-5 h-5 text-slate-400" />
            </button>
          </div>

          <div className="p-4 space-y-6">
            {/* Preview */}
            <div className="aspect-video rounded-lg overflow-hidden bg-[#1a1a1a] relative">
              {selectedSite.thumbnail ? (
                <Image
                  src={selectedSite.thumbnail}
                  alt={selectedSite.name}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <GlobeAltIcon className="w-12 h-12 text-slate-600" />
                </div>
              )}
            </div>

            {/* Info */}
            <div>
              <h4 className="font-medium text-lg">{selectedSite.name}</h4>
              <p className="text-sm text-slate-400">{selectedSite.slug}.e-quipe.app</p>
            </div>

            {/* Status */}
            <div className="p-3 rounded-lg bg-white/5 border border-white/5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Stato</span>
                <div className="flex items-center gap-1.5">
                  {getStatusIcon(selectedSite.status)}
                  <span className="text-sm font-medium">{getStatusLabel(selectedSite.status)}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              <Link
                href={`/editor/${selectedSite.id}`}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-all"
              >
                <PencilIcon className="w-4 h-4" />
                Modifica Sito
              </Link>
              
              {selectedSite.is_published ? (
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg font-medium transition-all">
                  <GlobeAltIcon className="w-4 h-4" />
                  Gestisci Dominio
                </button>
              ) : (
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-600/30 rounded-lg font-medium transition-all">
                  <RocketLaunchIcon className="w-4 h-4" />
                  Pubblica Sito
                </button>
              )}
            </div>

            {/* Stats */}
            <div className="pt-4 border-t border-white/5">
              <h5 className="text-sm font-medium text-slate-400 mb-3">Statistiche</h5>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-2xl font-semibold">0</p>
                  <p className="text-xs text-slate-500">Visite</p>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-2xl font-semibold">1</p>
                  <p className="text-xs text-slate-500">Pagine</p>
                </div>
              </div>
            </div>

            {/* Meta */}
            <div className="pt-4 border-t border-white/5 space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Creato il</span>
                <span className="text-slate-300">{formatDate(selectedSite.created_at)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Ultima modifica</span>
                <span className="text-slate-300">{formatDate(selectedSite.last_edited)}</span>
              </div>
            </div>
          </div>
        </aside>
      )}

      {/* Overlay per mobile */}
      {selectedSite && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSelectedSite(null)}
        />
      )}
    </div>
  );
}
