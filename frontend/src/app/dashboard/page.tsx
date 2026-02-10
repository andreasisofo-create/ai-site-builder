"use client";

export const dynamic = "force-dynamic";
import { useEffect, useState, Fragment } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { Menu, Transition } from "@headlessui/react";
import { useAuth, useRequireAuth } from "@/lib/auth-context";
import {
  PlusIcon,
  MagnifyingGlassIcon,
  BellIcon,
  Cog6ToothIcon,
  SparklesIcon,
  RocketLaunchIcon,
  GlobeAltIcon,
  PencilIcon,
  TrashIcon,
  EllipsisVerticalIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon,
  Squares2X2Icon,
  PhotoIcon,
  DocumentDuplicateIcon,
  PlayCircleIcon,
  ArrowRightIcon,
  ArrowUpRightIcon,
  ArrowRightStartOnRectangleIcon,
  UserCircleIcon,
  StarIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { fetchSites, deleteSite, Site, createCheckoutSession } from "@/lib/api";
import GenerationCounter from "@/components/GenerationCounter";

const SIDEBAR_ITEMS = [
  { icon: FolderIcon, label: "Progetti", active: true },
  { icon: Squares2X2Icon, label: "Templates", active: false },
  { icon: PhotoIcon, label: "Media", active: false },
  { icon: DocumentDuplicateIcon, label: "App", active: false },
  { icon: ClockIcon, label: "Attività", active: false },
];

const TEMPLATE_CATEGORIES = [
  {
    id: "restaurant",
    label: "Ristorante & Food",
    description: "Ristoranti, bar, pizzerie, pasticcerie",
    icon: "🍽️",
    image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&h=400&fit=crop",
    styles: 3,
  },
  {
    id: "agency",
    label: "Agenzia & Startup",
    description: "Agenzie digitali, startup tech, consulenza",
    icon: "🚀",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
    styles: 3,
  },
  {
    id: "portfolio",
    label: "Portfolio & Creativo",
    description: "Fotografi, designer, artisti, freelancer",
    icon: "🎨",
    image: "https://images.unsplash.com/photo-1545235617-9465d2a55698?w=600&h=400&fit=crop",
    styles: 3,
  },
  {
    id: "business",
    label: "Business & Professionale",
    description: "Studi legali, medici, consulenti, PMI",
    icon: "💼",
    image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&h=400&fit=crop",
    styles: 3,
  },
  {
    id: "custom",
    label: "Personalizzato",
    description: "Genera da zero senza template, scegli colori e sezioni",
    icon: "🎨",
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop",
    styles: 1,
  },
];

export default function Dashboard() {
  const { user, isLoading: authLoading, isAuthenticated, logout } = useAuth();
  useRequireAuth("/auth");
  const router = useRouter();
  const searchParams = useSearchParams();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(false); // Default to false to show UI immediately
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);
  const [isCheckingOut, setIsCheckingOut] = useState<string | null>(null);

  // Mostra notifica dopo pagamento riuscito
  useEffect(() => {
    const paymentStatus = searchParams.get("payment");
    const planName = searchParams.get("plan");
    if (paymentStatus === "success") {
      toast.success(`Piano ${planName === "premium" ? "Premium" : "Creazione Sito"} attivato con successo!`);
      router.replace("/dashboard");
    } else if (paymentStatus === "cancelled") {
      toast.error("Pagamento annullato");
      router.replace("/dashboard");
    }
  }, [searchParams, router]);

  // Carica siti dal backend
  useEffect(() => {
    if (isAuthenticated) {
      loadSites();
    }
  }, [isAuthenticated]);

  const loadSites = async () => {
    try {
      setLoading(true);
      const data = await fetchSites();
      setSites(data);
    } catch (error: any) {
      toast.error(error.message || "Errore nel caricamento siti");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSite = async (siteId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Sei sicuro di voler eliminare questo sito?")) return;

    try {
      setIsDeleting(siteId);
      await deleteSite(siteId);
      toast.success("Sito eliminato");
      setSites(sites.filter(s => s.id !== siteId));
      if (selectedSite?.id === siteId) {
        setSelectedSite(null);
      }
    } catch (error: any) {
      toast.error(error.message || "Errore nell'eliminazione");
    } finally {
      setIsDeleting(null);
    }
  };

  const handleUpgrade = async (plan: "base" | "premium") => {
    try {
      setIsCheckingOut(plan);
      const { checkout_url } = await createCheckoutSession(plan);
      window.location.href = checkout_url;
    } catch (error: any) {
      toast.error(error.message || "Errore durante il checkout");
      setIsCheckingOut(null);
    }
  };

  const createSite = (style?: string) => {
    if (style) {
      router.push("/dashboard/new");
    } else {
      router.push("/dashboard/new");
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("it-IT", {
      day: "numeric",
      month: "short",
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

  // Show loading screen while auth state is settling
  if (authLoading || (!isAuthenticated && typeof window !== "undefined" && !!localStorage.getItem("token"))) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const filteredSites = sites.filter((site) =>
    site.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex overflow-hidden">
      {/* Sidebar - Stile Wix Studio/VS Code */}
      <aside
        className={`fixed left-0 top-0 h-full bg-[#111] border-r border-white/5 transition-all duration-300 z-50 flex flex-col ${sidebarOpen ? "w-64" : "w-16"
          }`}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center px-4 border-b border-white/5">
          <Link href="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            {sidebarOpen && (
              <span className="font-semibold text-lg whitespace-nowrap">Studio</span>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          {SIDEBAR_ITEMS.map((item) => (
            <button
              key={item.label}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${item.active
                ? "bg-white/10 text-white"
                : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && (
                <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
              )}
              {!sidebarOpen && (
                <div className="absolute left-16 bg-white text-black px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none">
                  {item.label}
                </div>
              )}
            </button>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-white/5 space-y-4">
          {sidebarOpen ? (
            <GenerationCounter />
          ) : (
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-blue-500/30 flex items-center justify-center">
              <span className="text-xs font-bold text-blue-500">2</span>
            </div>
          )}

          {/* Admin link - subtle */}
          <a href="/admin" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors text-xs" title="Admin Panel">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            {sidebarOpen && <span>Admin</span>}
          </a>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center p-2 text-slate-500 hover:text-white transition-colors"
          >
            {sidebarOpen ? (
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider">
                <ChevronDownIcon className="w-3 h-3 rotate-90" />
                <span>Chiudi menu</span>
              </div>
            ) : (
              <ChevronDownIcon className="w-4 h-4 -rotate-90" />
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={`flex-1 flex flex-col h-screen transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-16"
          }`}
      >
        {/* Top Header */}
        <header className="h-16 px-8 border-b border-white/5 bg-[#0a0a0a]/80 backdrop-blur-xl flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-4 flex-1">
            <h1 className="text-lg font-semibold">Dashboard</h1>
            <div className="w-px h-4 bg-white/10 mx-2" />
            <div className="relative max-w-sm w-full">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Cerca nei tuoi siti..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-sm text-white focus:outline-none focus:border-blue-500/50 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white transition-colors relative">
              <BellIcon className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-[#0a0a0a]" />
            </button>

            <button
              onClick={() => createSite()}
              className="px-4 py-2 bg-white text-black rounded-full font-medium text-sm hover:bg-slate-200 transition-colors flex items-center gap-2"
            >
              <PlusIcon className="w-4 h-4" />
              Crea nuovo sito
            </button>

            <Menu as="div" className="relative">
              <Menu.Button className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-sm font-bold border border-white/10 cursor-pointer hover:ring-2 hover:ring-violet-400/50 transition-all">
                {user?.full_name?.[0] || user?.email?.[0] || "U"}
              </Menu.Button>

              <Transition
                as={Fragment}
                enter="transition ease-out duration-150"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-100"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
              >
                <Menu.Items className="absolute right-0 mt-2 w-72 origin-top-right rounded-xl bg-[#1a1a1a] border border-white/10 shadow-2xl shadow-black/50 z-50 overflow-hidden focus:outline-none">
                  {/* Header profilo */}
                  <div className="px-4 py-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-base font-bold flex-shrink-0">
                        {user?.full_name?.[0] || user?.email?.[0] || "U"}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-white truncate">
                          {user?.full_name || "Utente"}
                        </p>
                        <p className="text-xs text-slate-400 truncate">
                          {user?.email}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Abbonamento */}
                  <div className="px-4 py-3 border-b border-white/10">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400">Piano</span>
                      {(user as any)?.plan === "premium" || (user as any)?.is_premium ? (
                        <span className="px-2 py-0.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-400 text-xs font-medium flex items-center gap-1">
                          <StarIcon className="w-3 h-3" />
                          Premium
                        </span>
                      ) : (user as any)?.plan === "base" ? (
                        <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium">
                          Creazione Sito
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-400 text-xs font-medium">
                          Starter
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Logout */}
                  <div className="p-1">
                    <Menu.Item>
                      {({ active }) => (
                        <button
                          onClick={() => {
                            logout();
                            router.push("/auth");
                          }}
                          className={`${
                            active ? "bg-white/5" : ""
                          } w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 transition-colors`}
                        >
                          <ArrowRightStartOnRectangleIcon className="w-4 h-4" />
                          Esci
                        </button>
                      )}
                    </Menu.Item>
                  </div>
                </Menu.Items>
              </Transition>
            </Menu>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-12 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">

          {/* Hero Section */}
          <section className="relative rounded-2xl overflow-hidden border border-white/10 bg-[#111]">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-purple-900/20" />
            <div className="relative p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="max-w-xl space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium uppercase tracking-wider">
                  <SparklesIcon className="w-3 h-3" />
                  Nuovo Aggiornamento
                </div>
                <h2 className="text-3xl font-bold tracking-tight">Scopri Site Builder Studio</h2>
                <p className="text-slate-400 text-lg leading-relaxed">
                  Crea siti web straordinari con l'aiuto dell'AI. Parti da un template o lascia che l'intelligenza artificiale costruisca tutto per te in 60 secondi.
                </p>
                <div className="flex flex-wrap gap-4 pt-2">
                  <button
                    onClick={() => createSite()}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-medium transition-all shadow-lg shadow-blue-900/20"
                  >
                    Inizia a Creare
                  </button>
                  <button className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full font-medium transition-all flex items-center gap-2">
                    <PlayCircleIcon className="w-5 h-5" />
                    Guarda Tutorial
                  </button>
                </div>
              </div>
              <div className="relative w-full max-w-sm aspect-video rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-black/50 hidden md:block">
                <Image
                  src="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=800&q=80"
                  alt="Studio Preview"
                  fill
                  className="object-cover opacity-80"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                    <PlayCircleIcon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Upgrade Banner - mostra solo per piano free */}
          {(!user || (user as any)?.plan === "free" || !(user as any)?.plan) && (
            <section className="relative rounded-2xl overflow-hidden border border-violet-500/20 bg-gradient-to-r from-violet-900/20 via-blue-900/20 to-purple-900/20">
              <div className="relative p-8">
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <StarIcon className="w-5 h-5 text-amber-400" />
                      <h3 className="text-lg font-semibold">Sblocca tutto il potenziale</h3>
                    </div>
                    <p className="text-slate-400 text-sm max-w-lg">
                      Passa a un piano a pagamento per pubblicare il tuo sito, ottenere piu generazioni AI e modifiche illimitate.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => handleUpgrade("base")}
                      disabled={isCheckingOut !== null}
                      className="px-5 py-2.5 bg-white/10 border border-white/20 rounded-full text-sm font-medium hover:bg-white/20 transition-all disabled:opacity-50 flex items-center gap-2"
                    >
                      {isCheckingOut === "base" ? (
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                      ) : null}
                      Creazione Sito - 200
                    </button>
                    <button
                      onClick={() => handleUpgrade("premium")}
                      disabled={isCheckingOut !== null}
                      className="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-blue-600 rounded-full text-sm font-semibold hover:from-violet-500 hover:to-blue-500 transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-violet-900/30"
                    >
                      {isCheckingOut === "premium" ? (
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                      ) : null}
                      Premium - 500
                    </button>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Templates Section */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Inizia da un Template AI</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {TEMPLATE_CATEGORIES.map((category) => (
                <div
                  key={category.id}
                  onClick={() => router.push(`/dashboard/new?template=${category.id}`)}
                  className="group relative aspect-[4/3] rounded-xl border border-white/10 bg-[#111] overflow-hidden cursor-pointer hover:border-blue-500/30 hover:shadow-2xl hover:shadow-blue-900/10 transition-all"
                >
                  <Image
                    src={category.image}
                    alt={category.label}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent p-4 flex flex-col justify-end">
                    <div className="text-2xl mb-1">{category.icon}</div>
                    <h4 className="font-semibold text-white">{category.label}</h4>
                    <p className="text-xs text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity translate-y-1 group-hover:translate-y-0 delay-75">
                      {category.description} &middot; {category.styles} stili
                    </p>
                  </div>
                  <div className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowRightIcon className="w-4 h-4 text-white" />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* My Sites Section */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">I Tuoi Progetti</h3>
              <div className="flex gap-2">
                <button className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors">
                  <Bars3Icon className="w-5 h-5" />
                </button>
                <button className="p-2 bg-white/10 rounded-lg text-white transition-colors">
                  <Squares2X2Icon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {filteredSites.length === 0 ? (
              <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
                <div className="w-16 h-16 rounded-full bg-white/5 mx-auto flex items-center justify-center mb-4">
                  <FolderIcon className="w-8 h-8 text-slate-500" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Nessun progetto trovato</h3>
                <p className="text-slate-400 mb-6">Inizia creando il tuo primo sito web con l'AI</p>
                <button
                  onClick={() => createSite()}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-medium transition-all"
                >
                  Crea Primo Progetto
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredSites.map((site) => (
                  <div
                    key={site.id}
                    onClick={() => setSelectedSite(site)}
                    className="group bg-[#111] rounded-xl border border-white/5 overflow-hidden hover:border-white/20 transition-all cursor-pointer hover:shadow-xl"
                  >
                    {/* Thumbnail */}
                    <div className="aspect-video relative bg-[#1a1a1a] overflow-hidden">
                      {site.thumbnail ? (
                        <Image
                          src={site.thumbnail}
                          alt={site.name}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <GlobeAltIcon className="w-12 h-12 text-slate-700" />
                        </div>
                      )}

                      {/* Overlay Actions */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 backdrop-blur-sm">
                        <Link
                          href={`/editor/${site.id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="px-4 py-2 bg-white text-black rounded-full text-sm font-medium hover:scale-105 transition-transform"
                        >
                          Modifica
                        </Link>
                        <button
                          onClick={(e) => handleDeleteSite(site.id, e)}
                          disabled={isDeleting === site.id}
                          className="px-4 py-2 bg-red-500/80 text-white rounded-full text-sm font-medium hover:bg-red-500 hover:scale-105 transition-all disabled:opacity-50"
                        >
                          {isDeleting === site.id ? "..." : "Elimina"}
                        </button>
                        {site.is_published && (
                          <Link
                            href={`https://${site.slug}.e-quipe.app`}
                            target="_blank"
                            onClick={(e) => e.stopPropagation()}
                            className="p-2 bg-white/20 text-white rounded-full hover:bg-white/30 transition-colors"
                          >
                            <ArrowUpRightIcon className="w-5 h-5" />
                          </Link>
                        )}
                      </div>

                      {/* Status Badge */}
                      <div className="absolute top-3 left-3 px-2 py-1 bg-black/80 backdrop-blur-md rounded-md border border-white/10 flex items-center gap-2">
                        {getStatusIcon(site.status)}
                        <span className="text-xs font-medium text-slate-200 capitalize">{site.status}</span>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-white group-hover:text-blue-400 transition-colors">{site.name}</h4>
                          <p className="text-sm text-slate-500 mt-0.5">{site.slug}.e-quipe.app</p>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); /* Menu logic */ }}
                          className="p-1 text-slate-500 hover:text-white transition-colors"
                        >
                          <EllipsisVerticalIcon className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="mt-4 flex items-center justify-between text-xs text-slate-600">
                        <span>Modificato {formatDate(site.updated_at || site.created_at)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Resources Section */}
          <section>
            <h3 className="text-xl font-semibold mb-6">Guarda video tutorial</h3>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                "Esplora l'editor di Site Builder",
                "Come ottimizzare il SEO",
                "Collegare un dominio personalizzato"
              ].map((title, idx) => (
                <div key={idx} className="flex gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors cursor-pointer group">
                  <div className="w-32 aspect-video bg-black/50 rounded-lg border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:border-blue-500/30 transition-colors">
                    <PlayCircleIcon className="w-8 h-8 text-slate-600 group-hover:text-blue-500 transition-colors" />
                  </div>
                  <div className="flex flex-col justify-center">
                    <h4 className="text-sm font-medium text-slate-200 group-hover:text-white mb-1">{title}</h4>
                    <p className="text-xs text-blue-400 flex items-center gap-1 group-hover:underline">
                      Riproduci video
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>
      </main>

      {/* Detail Overlay / Drawer (Opzionale, simile a prima ma più pulito) */}
      {selectedSite && (
        <aside className="fixed right-0 top-0 h-full w-96 bg-[#111] border-l border-white/10 z-[60] shadow-2xl transform transition-transform animate-in slide-in-from-right duration-200">
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="h-16 flex items-center justify-between px-6 border-b border-white/5">
              <h3 className="font-semibold">Dettagli Sito</h3>
              <button onClick={() => setSelectedSite(null)} className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Preview Large */}
              <div className="aspect-video rounded-xl overflow-hidden bg-black/50 border border-white/10 relative group">
                {selectedSite.thumbnail && (
                  <Image src={selectedSite.thumbnail} alt={selectedSite.name} fill className="object-cover" />
                )}
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Link href={`/editor/${selectedSite.id}`} className="px-6 py-2 bg-white text-black rounded-full font-medium transform hover:scale-105 transition-all">
                    Apri Editor
                  </Link>
                </div>
              </div>

              {/* Info Block */}
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Nome Sito</label>
                  <div className="flex items-center gap-2 mt-1">
                    <h2 className="text-2xl font-bold">{selectedSite.name}</h2>
                    <button className="p-1 hover:bg-white/10 rounded"><PencilIcon className="w-4 h-4 text-slate-400" /></button>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Dominio</label>
                  <a href={`https://${selectedSite.slug}.e-quipe.app`} target="_blank" className="flex items-center gap-2 mt-1 text-blue-400 hover:underline">
                    {selectedSite.slug}.e-quipe.app
                    <ArrowUpRightIcon className="w-4 h-4" />
                  </a>
                </div>
              </div>

              {/* Actions Grid */}
              <div className="grid grid-cols-2 gap-3">
                <Link href={`/editor/${selectedSite.id}`} className="col-span-2 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-colors">
                  <PencilIcon className="w-4 h-4" />
                  Modifica Sito
                </Link>
                <button
                  onClick={(e) => handleDeleteSite(selectedSite.id, e)}
                  className="py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  {isDeleting === selectedSite.id ? <div className="w-4 h-4 border-2 border-current rounded-full animate-spin" /> : <TrashIcon className="w-4 h-4" />}
                  Elimina
                </button>
                <button className="py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors">
                  <Cog6ToothIcon className="w-4 h-4" />
                  Impostazioni
                </button>
              </div>
            </div>
          </div>
        </aside>
      )}

    </div>
  );
}
