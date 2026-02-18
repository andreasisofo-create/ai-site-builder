"use client";

export const dynamic = "force-dynamic";
import { Suspense, useEffect, useState, Fragment } from "react";
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
  CheckCircleIcon,
  ExclamationCircleIcon,
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon,
  Squares2X2Icon,
  PlayCircleIcon,
  ArrowRightIcon,
  ArrowUpRightIcon,
  ArrowRightStartOnRectangleIcon,
  UserCircleIcon,
  StarIcon,
  LockClosedIcon,
  CreditCardIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { fetchSites, deleteSite, Site, getMySubscriptions, cancelSubscription, UserSubscription } from "@/lib/api";
import GenerationCounter from "@/components/GenerationCounter";
import { TEMPLATE_CATEGORIES, generateStylePreviewHtml } from "@/lib/templates";
import { useLanguage } from "@/lib/i18n";
import LanguageSwitcher from "@/components/LanguageSwitcher";

const SIDEBAR_ITEMS = (language: string) => [
  { icon: FolderIcon, label: language === "en" ? "Projects" : "Progetti", active: true },
  { icon: CreditCardIcon, label: language === "en" ? "My Services" : "I Miei Servizi", active: false },
  { icon: RocketLaunchIcon, label: language === "en" ? "Plans & Services" : "Piani e Servizi", active: false },
  { icon: Squares2X2Icon, label: "Templates", active: false },
];

const FILTER_TABS = (language: string) => [
  { id: "all", label: language === "en" ? "All" : "Tutti" },
  ...TEMPLATE_CATEGORIES.filter(c => c.id !== "custom").map(c => ({ id: c.id, label: c.label.split(" & ")[0] })),
];

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center"><div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>}>
      <Dashboard />
    </Suspense>
  );
}

function Dashboard() {
  const { user, isLoading: authLoading, isAuthenticated, logout } = useAuth();
  useRequireAuth("/auth");
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language } = useLanguage();
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(false); // Default to false to show UI immediately
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);
  const [activeFilter, setActiveFilter] = useState("all");
  const [showAllTemplates, setShowAllTemplates] = useState(false);
  const [hoveredTemplate, setHoveredTemplate] = useState<string | null>(null);
  const [isDesktop, setIsDesktop] = useState(false);
  const [subscriptions, setSubscriptions] = useState<UserSubscription[]>([]);
  const [subscriptionsLoading, setSubscriptionsLoading] = useState(false);
  const [cancellingId, setCancellingId] = useState<number | null>(null);

  // Detect desktop (hover-capable) device for template hover preview
  useEffect(() => {
    const mq = window.matchMedia("(hover: hover)");
    setIsDesktop(mq.matches);
    const handler = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  // Mostra notifica dopo pagamento riuscito
  useEffect(() => {
    const paymentStatus = searchParams.get("payment");
    const planName = searchParams.get("plan");
    const serviceName = searchParams.get("service");
    if (paymentStatus === "success" && serviceName) {
      // Service checkout success
      const displayName = serviceName.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
      toast.success(language === "en" ? `Service ${displayName} activated!` : `Servizio ${displayName} attivato!`);
      router.replace("/dashboard");
      // Reload subscriptions
      loadSubscriptions();
    } else if (paymentStatus === "success") {
      const planText = language === "en"
        ? (planName === "premium" ? "Premium" : "Site Creation")
        : (planName === "premium" ? "Premium" : "Creazione Sito");
      toast.success(language === "en" ? `${planText} plan activated successfully!` : `Piano ${planText} attivato con successo!`);
      router.replace("/dashboard");
    } else if (paymentStatus === "cancelled") {
      toast.error(language === "en" ? "Payment cancelled" : "Pagamento annullato");
      router.replace("/dashboard");
    }
  }, [searchParams, router, language]);

  // Carica siti dal backend
  useEffect(() => {
    if (isAuthenticated) {
      loadSites();
      loadSubscriptions();
    }
  }, [isAuthenticated]);

  const loadSites = async () => {
    try {
      setLoading(true);
      const data = await fetchSites();
      setSites(data);
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "Error loading sites" : "Errore nel caricamento siti"));
    } finally {
      setLoading(false);
    }
  };

  const loadSubscriptions = async () => {
    try {
      setSubscriptionsLoading(true);
      const data = await getMySubscriptions();
      setSubscriptions(data);
    } catch (error: any) {
      // Silently fail - subscriptions section will show empty state
      console.error("Failed to load subscriptions:", error);
    } finally {
      setSubscriptionsLoading(false);
    }
  };

  const handleCancelSubscription = async (sub: UserSubscription) => {
    const confirmMsg = language === "en"
      ? `Are you sure you want to cancel "${sub.service_name_en}"? This action cannot be undone.`
      : `Sei sicuro di voler annullare "${sub.service_name}"? Questa azione non puo' essere annullata.`;
    if (!confirm(confirmMsg)) return;

    try {
      setCancellingId(sub.id);
      await cancelSubscription(sub.id);
      toast.success(language === "en" ? "Subscription cancelled" : "Abbonamento annullato");
      await loadSubscriptions();
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "Error cancelling subscription" : "Errore nell'annullamento"));
    } finally {
      setCancellingId(null);
    }
  };

  const handleDeleteSite = async (siteId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(language === "en" ? "Are you sure you want to delete this site?" : "Sei sicuro di voler eliminare questo sito?")) return;

    try {
      setIsDeleting(siteId);
      await deleteSite(siteId);
      toast.success(language === "en" ? "Site deleted" : "Sito eliminato");
      setSites(sites.filter(s => s.id !== siteId));
      if (selectedSite?.id === siteId) {
        setSelectedSite(null);
      }
    } catch (error: any) {
      toast.error(error.message || (language === "en" ? "Error deleting site" : "Errore nell'eliminazione"));
    } finally {
      setIsDeleting(null);
    }
  };

  const createSite = (styleId?: string) => {
    if (styleId) {
      router.push(`/dashboard/new?style=${styleId}`);
    } else {
      router.push("/dashboard/new");
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return new Intl.DateTimeFormat(language === "en" ? "en-US" : "it-IT", {
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
      {/* Mobile sidebar backdrop */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Hidden on mobile, visible on desktop */}
      <aside
        className={`fixed left-0 top-0 h-full bg-[#111] border-r border-white/5 transition-all duration-300 flex flex-col
          ${mobileSidebarOpen ? "translate-x-0 z-50" : "-translate-x-full z-50"}
          lg:translate-x-0 ${sidebarOpen ? "w-64" : "lg:w-16 w-64"}
        `}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center px-4 border-b border-white/5 justify-between">
          <Link href="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            {(sidebarOpen || mobileSidebarOpen) && (
              <span className="font-semibold text-lg whitespace-nowrap">Studio</span>
            )}
          </Link>
          {/* Close button - mobile only */}
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          {SIDEBAR_ITEMS(language).map((item) => (
            <button
              key={item.label}
              onClick={() => {
                const projectLabel = language === "en" ? "Projects" : "Progetti";
                const servicesLabel = language === "en" ? "My Services" : "I Miei Servizi";
                const storeLabel = language === "en" ? "Plans & Services" : "Piani e Servizi";
                const comingSoon = language === "en" ? "Coming Soon" : "Prossimamente";

                if (item.label === projectLabel) {
                  document.getElementById("section-progetti")?.scrollIntoView({ behavior: "smooth" });
                } else if (item.label === servicesLabel) {
                  document.getElementById("section-servizi")?.scrollIntoView({ behavior: "smooth" });
                } else if (item.label === storeLabel) {
                  router.push("/pacchetti");
                } else if (item.label === "Templates") {
                  document.getElementById("section-templates")?.scrollIntoView({ behavior: "smooth" });
                } else {
                  toast(`${item.label}: ${comingSoon}`, { icon: "\u{1F6A7}" });
                }
                setMobileSidebarOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group ${item.active
                ? "bg-white/10 text-white"
                : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {(sidebarOpen || mobileSidebarOpen) && (
                <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
              )}
              {!sidebarOpen && !mobileSidebarOpen && (
                <div className="absolute left-16 bg-white text-black px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none">
                  {item.label}
                </div>
              )}
            </button>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-white/5 space-y-4">
          {(sidebarOpen || mobileSidebarOpen) ? (
            <GenerationCounter />
          ) : (
            <div className="w-8 h-8 mx-auto rounded-full border-2 border-blue-500/30 flex items-center justify-center">
              <span className="text-xs font-bold text-blue-500">2</span>
            </div>
          )}

          {/* Admin link - subtle */}
          <a href="/admin" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors text-xs" title="Admin Panel">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            {(sidebarOpen || mobileSidebarOpen) && <span>Admin</span>}
          </a>

          <button
            onClick={() => {
              // On mobile, close the overlay; on desktop, toggle sidebar width
              if (window.innerWidth < 1024) {
                setMobileSidebarOpen(false);
              } else {
                setSidebarOpen(!sidebarOpen);
              }
            }}
            className="w-full flex items-center justify-center p-2 text-slate-500 hover:text-white transition-colors"
          >
            {(sidebarOpen || mobileSidebarOpen) ? (
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider">
                <ChevronDownIcon className="w-3 h-3 rotate-90" />
                <span>{language === "en" ? "Close menu" : "Chiudi menu"}</span>
              </div>
            ) : (
              <ChevronDownIcon className="w-4 h-4 -rotate-90" />
            )}
          </button>

          {/* Language Switcher */}
          {(sidebarOpen || mobileSidebarOpen) && (
            <div className="px-4 pb-2 flex justify-center">
              <LanguageSwitcher />
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={`flex-1 flex flex-col h-screen transition-all duration-300 ml-0 ${sidebarOpen ? "lg:ml-64" : "lg:ml-16"
          }`}
      >
        {/* Top Header */}
        <header className="h-16 px-4 lg:px-8 border-b border-white/5 bg-[#0a0a0a]/80 backdrop-blur-xl flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 lg:gap-4 flex-1 min-w-0">
            {/* Hamburger menu - mobile only */}
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors flex-shrink-0"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>

            <h1 className="text-lg font-semibold flex-shrink-0">Dashboard</h1>
            <div className="w-px h-4 bg-white/10 mx-1 lg:mx-2 hidden sm:block" />
            <div className="relative max-w-sm w-full hidden sm:block">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder={language === "en" ? "Search your sites..." : "Cerca nei tuoi siti..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-sm text-white focus:outline-none focus:border-blue-500/50 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 lg:gap-4">
            <button className="p-2 text-slate-400 hover:text-white transition-colors relative">
              <BellIcon className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-[#0a0a0a]" />
            </button>

            <button
              onClick={() => createSite()}
              className="px-3 lg:px-4 py-2 bg-white text-black rounded-full font-medium text-sm hover:bg-slate-200 transition-colors flex items-center gap-2"
            >
              <PlusIcon className="w-4 h-4" />
              <span className="hidden sm:inline">{language === "en" ? "Create new site" : "Crea nuovo sito"}</span>
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
                          {user?.full_name || (language === "en" ? "User" : "Utente")}
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
                      <span className="text-xs text-slate-400">{language === "en" ? "Plan" : "Piano"}</span>
                      {(user as any)?.plan === "premium" || (user as any)?.is_premium ? (
                        <span className="px-2 py-0.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 text-amber-400 text-xs font-medium flex items-center gap-1">
                          <StarIcon className="w-3 h-3" />
                          Premium
                        </span>
                      ) : (user as any)?.plan === "base" ? (
                        <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-medium">
                          {language === "en" ? "Site Creation" : "Creazione Sito"}
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
                          {language === "en" ? "Logout" : "Esci"}
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
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-8 lg:space-y-12 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">

          {/* Hero: Choose Your Path */}
          <section className="grid md:grid-cols-2 gap-6">
            {/* Card 1: AI Builder */}
            <button onClick={() => createSite()} className="group relative rounded-2xl p-8 text-left transition-all hover:-translate-y-1 hover:shadow-2xl border border-white/10 bg-gradient-to-br from-blue-950/80 to-indigo-950/50 hover:border-blue-500/30">
              <div className="w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6">
                <SparklesIcon className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{language === "en" ? "Smart Builder" : "Costruttore Intelligente"}</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">{language === "en" ? "Answer a few questions about your business and AI creates your complete website in 60 seconds." : "Rispondi a poche domande sulla tua attivita' e l'AI crea il tuo sito completo in 60 secondi."}</p>
              <span className="inline-flex items-center gap-2 text-blue-400 text-sm font-medium group-hover:gap-3 transition-all">
                {language === "en" ? "Start creating" : "Inizia a creare"}
                <ArrowRightIcon className="w-4 h-4" />
              </span>
            </button>

            {/* Card 2: Browse Templates */}
            <button onClick={() => { setShowAllTemplates(true); setTimeout(() => document.getElementById("section-templates")?.scrollIntoView({ behavior: "smooth" }), 100); }} className="group relative rounded-2xl p-8 text-left transition-all hover:-translate-y-1 hover:shadow-2xl border border-white/10 bg-gradient-to-br from-violet-950/80 to-purple-950/50 hover:border-violet-500/30">
              <div className="w-14 h-14 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-6">
                <Squares2X2Icon className="w-7 h-7 text-violet-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{language === "en" ? "Choose a Template" : "Scegli un Template"}</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-6">{language === "en" ? "Browse 19 professional designs and customize with your content." : "Sfoglia 19 design professionali e personalizzali con i tuoi contenuti."}</p>
              <span className="inline-flex items-center gap-2 text-violet-400 text-sm font-medium group-hover:gap-3 transition-all">
                {language === "en" ? "Browse templates" : "Sfoglia i template"}
                <ArrowRightIcon className="w-4 h-4" />
              </span>
            </button>
          </section>

          {/* Unlock Potential CTA */}
          <section id="section-store" className="mb-4">
            <div className="relative rounded-2xl p-8 md:p-10 border border-white/10 bg-gradient-to-br from-blue-950/60 to-violet-950/40 overflow-hidden">
              {/* Background decoration */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-violet-500/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />

              <div className="relative z-10 text-center max-w-xl mx-auto">
                <div className="w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-5">
                  <RocketLaunchIcon className="w-7 h-7 text-blue-400" />
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-white mb-3">
                  {language === "en" ? "Unlock the full potential" : "Sblocca tutto il potenziale"}
                </h3>
                <p className="text-slate-400 text-sm md:text-base mb-6 leading-relaxed">
                  {language === "en"
                    ? "Choose a package to get your professional website, ads management, and AI content — all in one solution."
                    : "Scegli un pacchetto per ottenere il tuo sito professionale, gestione ads e contenuti AI — tutto in un'unica soluzione."}
                </p>
                <Link
                  href="/pacchetti"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-semibold text-sm transition-colors"
                >
                  {language === "en" ? "Explore Plans & Services" : "Esplora Piani e Servizi"}
                  <ArrowRightIcon className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </section>

          {/* My Sites Section */}
          <section id="section-progetti">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">
                {language === "en" ? "Your Projects" : "I Tuoi Progetti"}
              </h3>
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
              <div className="text-center py-16 border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
                <div className="w-14 h-14 rounded-full bg-white/5 mx-auto flex items-center justify-center mb-4">
                  <FolderIcon className="w-7 h-7 text-slate-500" />
                </div>
                <h3 className="text-base font-medium text-white mb-1">
                  {language === "en" ? "No projects yet" : "Nessun progetto ancora"}
                </h3>
                <p className="text-slate-500 text-sm mb-5">
                  {language === "en" ? "Create your first website with AI" : "Crea il tuo primo sito web con l'AI"}
                </p>
                <button
                  onClick={() => createSite()}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-sm font-medium transition-all"
                >
                  {language === "en" ? "Create First Project" : "Crea Primo Progetto"}
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
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 backdrop-blur-sm">
                        <Link
                          href={`/editor/${site.id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="px-4 py-2 bg-white text-black rounded-full text-sm font-medium hover:scale-105 transition-transform"
                        >
                          {language === "en" ? "Edit" : "Modifica"}
                        </Link>
                        <button
                          onClick={(e) => handleDeleteSite(site.id, e)}
                          disabled={isDeleting === site.id}
                          className="px-4 py-2 bg-red-500/80 text-white rounded-full text-sm font-medium hover:bg-red-500 hover:scale-105 transition-all disabled:opacity-50"
                        >
                          {isDeleting === site.id ? "..." : (language === "en" ? "Delete" : "Elimina")}
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
                      <div className="absolute top-3 left-3 px-2 py-1 bg-black/80 backdrop-blur-md rounded-md border border-white/10 flex items-center gap-2">
                        {getStatusIcon(site.status)}
                        <span className="text-xs font-medium text-slate-200 capitalize">{
                          language === "en"
                            ? { ready: "Ready", published: "Published", generating: "Generating", draft: "Draft", error: "Error" }[site.status] || site.status
                            : { ready: "Pronto", published: "Pubblicato", generating: "In generazione", draft: "Bozza", error: "Errore" }[site.status] || site.status
                        }</span>
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-white group-hover:text-blue-400 transition-colors">{site.name}</h4>
                          <p className="text-sm text-slate-500 mt-0.5">{site.slug}.e-quipe.app</p>
                        </div>
                        <button
                          onClick={(e) => { e.stopPropagation(); }}
                          className="p-1 text-slate-500 hover:text-white transition-colors"
                        >
                          <EllipsisVerticalIcon className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
                        <span>{language === "en" ? "Modified" : "Modificato"} {formatDate(site.updated_at || site.created_at)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* My Services Section */}
          <section id="section-servizi">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">
                {language === "en" ? "My Services" : "I Miei Servizi"}
              </h3>
            </div>

            {subscriptionsLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : subscriptions.length === 0 ? (
              <div className="text-center py-16 border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
                <div className="w-14 h-14 rounded-full bg-white/5 mx-auto flex items-center justify-center mb-4">
                  <CreditCardIcon className="w-7 h-7 text-slate-500" />
                </div>
                <h3 className="text-base font-medium text-white mb-1">
                  {language === "en" ? "No active services" : "Nessun servizio attivo"}
                </h3>
                <p className="text-slate-500 text-sm mb-5">
                  {language === "en"
                    ? "Explore our services and find the right one for your business"
                    : "Esplora i nostri servizi e trova quello giusto per la tua attivita'"}
                </p>
                <Link
                  href="/prezzi"
                  className="inline-flex px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-full text-sm font-medium transition-all"
                >
                  {language === "en" ? "Explore Services" : "Esplora Servizi"}
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {subscriptions.map((sub) => {
                  const name = language === "en" ? sub.service_name_en : sub.service_name;
                  const priceEuros = (sub.monthly_amount_cents / 100).toFixed(sub.monthly_amount_cents % 100 === 0 ? 0 : 2);
                  const priceLabel = language === "en" ? `\u20AC${priceEuros}/month` : `\u20AC${priceEuros}/mese`;

                  let statusBadge: { text: string; className: string };
                  switch (sub.status) {
                    case "active":
                      statusBadge = {
                        text: language === "en" ? "Active" : "Attivo",
                        className: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
                      };
                      break;
                    case "pending_setup":
                      statusBadge = {
                        text: language === "en" ? "Pending" : "In attesa",
                        className: "bg-amber-500/10 border-amber-500/30 text-amber-400",
                      };
                      break;
                    case "cancelled":
                      statusBadge = {
                        text: language === "en" ? "Cancelled" : "Annullato",
                        className: "bg-red-500/10 border-red-500/30 text-red-400",
                      };
                      break;
                    default:
                      statusBadge = {
                        text: sub.status,
                        className: "bg-white/5 border-white/10 text-slate-400",
                      };
                  }

                  let features: string[] = [];
                  try {
                    const raw = language === "en" ? sub.features_en_json : sub.features_json;
                    if (raw) features = JSON.parse(raw);
                  } catch {
                    // ignore parse errors
                  }

                  const nextBilling = sub.next_billing_date
                    ? new Intl.DateTimeFormat(language === "en" ? "en-US" : "it-IT", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      }).format(new Date(sub.next_billing_date))
                    : "\u2014";

                  return (
                    <div
                      key={sub.id}
                      className="bg-[#161616] border border-white/5 rounded-xl p-5 flex flex-col"
                    >
                      {/* Header: name + status */}
                      <div className="flex items-start justify-between mb-4">
                        <h4 className="font-semibold text-white text-base">{name}</h4>
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusBadge.className}`}
                        >
                          {statusBadge.text}
                        </span>
                      </div>

                      {/* Price */}
                      <div className="mb-4">
                        <span className="text-2xl font-bold text-white">{priceLabel}</span>
                      </div>

                      {/* Next billing */}
                      <div className="mb-4 text-sm">
                        <span className="text-slate-500">
                          {language === "en" ? "Next billing:" : "Prossimo rinnovo:"}
                        </span>{" "}
                        <span className="text-slate-300">{nextBilling}</span>
                      </div>

                      {/* Features */}
                      {features.length > 0 && (
                        <ul className="space-y-2 mb-5 flex-1">
                          {features.map((feat, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-slate-400">
                              <CheckCircleIcon className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                              <span>{feat}</span>
                            </li>
                          ))}
                        </ul>
                      )}

                      {/* Cancel button - only for active subscriptions */}
                      {sub.status === "active" && (
                        <button
                          onClick={() => handleCancelSubscription(sub)}
                          disabled={cancellingId === sub.id}
                          className="mt-auto w-full py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                          {cancellingId === sub.id ? (
                            <div className="w-4 h-4 border-2 border-red-400/40 border-t-red-400 rounded-full animate-spin" />
                          ) : null}
                          {language === "en" ? "Cancel" : "Annulla"}
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* Template Gallery Section */}
          <section id="section-templates">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold mb-1">
                  {showAllTemplates
                    ? (language === "en" ? "All Templates" : "Tutti i Template")
                    : (language === "en" ? "Trending Templates" : "Template in Tendenza")}
                </h3>
                {!showAllTemplates && (
                  <p className="text-slate-400 text-sm">
                    {language === "en" ? "Popular designs to get you started" : "Design popolari per iniziare"}
                  </p>
                )}
              </div>
              <button
                onClick={() => setShowAllTemplates(!showAllTemplates)}
                className="px-4 py-2 rounded-full text-sm font-medium bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white transition-all flex items-center gap-2"
              >
                {showAllTemplates
                  ? (language === "en" ? "Show less" : "Mostra meno")
                  : (language === "en" ? "See all" : "Vedi tutti")}
                <ArrowRightIcon className={`w-3.5 h-3.5 transition-transform ${showAllTemplates ? "rotate-90" : ""}`} />
              </button>
            </div>

            {/* Filter Tabs - only when showing all */}
            {showAllTemplates && (
              <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
                {FILTER_TABS(language).map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveFilter(tab.id)}
                    className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                      activeFilter === tab.id
                        ? "bg-white text-black"
                        : "bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            )}

            {/* Template Grid with lock overlay for free users */}
            <div className="relative">
              {((user as any)?.plan === "free" || !(user as any)?.plan) && (
                <div className="absolute inset-0 z-20 bg-black/50 backdrop-blur-[3px] rounded-2xl flex flex-col items-center justify-center">
                  <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                    <LockClosedIcon className="w-8 h-8 text-slate-400" />
                  </div>
                  <p className="text-lg text-white font-semibold mb-1">
                    {language === "en" ? "Premium Templates" : "Template Premium"}
                  </p>
                  <p className="text-slate-400 text-sm mb-5 text-center max-w-sm">
                    {language === "en"
                      ? "Unlock all professional templates with a Base or Premium plan"
                      : "Sblocca tutti i template professionali con un piano Base o Premium"}
                  </p>
                  <Link
                    href="/checkout?service=pack-presenza"
                    className="px-6 py-2.5 bg-violet-600 hover:bg-violet-500 text-white rounded-full text-sm font-semibold transition-colors inline-block"
                  >
                    {language === "en" ? "Unlock Templates" : "Sblocca Templates"}
                  </Link>
                </div>
              )}

              <div className={`grid gap-6 ${showAllTemplates ? "grid-cols-1 md:grid-cols-2 xl:grid-cols-3" : "grid-cols-2 md:grid-cols-4"}`}>
                {(() => {
                  const allTemplates = TEMPLATE_CATEGORIES
                    .filter(cat => !showAllTemplates || activeFilter === "all" || cat.id === activeFilter)
                    .flatMap(cat =>
                      cat.styles.map(style => ({ style, categoryLabel: cat.label, categoryId: cat.id }))
                    );
                  const templatesToShow = showAllTemplates ? allTemplates : allTemplates.slice(0, 4);
                  return templatesToShow.map(({ style, categoryLabel }) => (
                    <div
                      key={style.id}
                      onClick={() => {
                        const userPlan = (user as any)?.plan || "free";
                        if (userPlan === "free" || !userPlan) {
                          toast(language === "en" ? "Available with Base or Premium plan" : "Disponibile con piano Base o Premium", { icon: "🔒" });
                          return;
                        }
                        router.push(`/dashboard/new?style=${style.id}`);
                      }}
                      className="group relative rounded-xl border border-white/10 bg-[#111] overflow-hidden cursor-pointer transition-all hover:border-blue-500/30 hover:shadow-2xl hover:shadow-blue-900/10 hover:scale-[1.02]"
                      onMouseEnter={() => { if (isDesktop) setHoveredTemplate(style.id); }}
                      onMouseLeave={() => { if (isDesktop) setHoveredTemplate(null); }}
                    >
                      {/* Iframe Preview */}
                      <div className="relative aspect-[16/9] overflow-hidden bg-[#0a0a0a]">
                        <iframe
                          srcDoc={generateStylePreviewHtml(style, categoryLabel)}
                          className="w-[1200px] h-[800px] border-0 pointer-events-none"
                          style={{
                            transform: `scale(0.35) translateY(${hoveredTemplate === style.id ? -200 : 0}px)`,
                            transformOrigin: "top left",
                            transition: hoveredTemplate === style.id
                              ? "transform 3s ease-in-out"
                              : "transform 0.5s ease-out",
                          }}
                          title={style.label}
                          loading="lazy"
                          sandbox="allow-same-origin"
                        />
                        {/* Gradient overlay bottom */}
                        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#111] to-transparent" />
                      </div>

                      {/* Info Bar */}
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-white text-sm">{style.label}</h4>
                          <span className="text-xs text-slate-500 bg-white/5 px-2 py-0.5 rounded-full">{categoryLabel.split(" & ")[0]}</span>
                        </div>
                        <p className="text-xs text-slate-500 mb-3">{style.description}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-1.5">
                            <div className="w-4 h-4 rounded-full border border-white/10" style={{ background: style.primaryColor }} />
                            <div className="w-4 h-4 rounded-full border border-white/10" style={{ background: style.secondaryColor }} />
                          </div>
                          <div className="flex items-center gap-1 text-xs text-slate-500 group-hover:text-blue-400 transition-colors">
                            <span>{language === "en" ? "Use template" : "Usa template"}</span>
                            <ArrowRightIcon className="w-3 h-3" />
                          </div>
                        </div>
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          </section>

          {/* Resources Section */}
          <section>
            <h3 className="text-xl font-semibold mb-6">
              {language === "en" ? "Watch video tutorials" : "Guarda video tutorial"}
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              {(language === "en" ? [
                "Explore the Site Builder editor",
                "How to optimize SEO",
                "Connect a custom domain"
              ] : [
                "Esplora l'editor di Site Builder",
                "Come ottimizzare il SEO",
                "Collegare un dominio personalizzato"
              ]).map((title, idx) => (
                <div key={idx} className="flex gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors cursor-pointer group">
                  <div className="w-32 aspect-video bg-black/50 rounded-lg border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:border-blue-500/30 transition-colors">
                    <PlayCircleIcon className="w-8 h-8 text-slate-600 group-hover:text-blue-500 transition-colors" />
                  </div>
                  <div className="flex flex-col justify-center">
                    <h4 className="text-sm font-medium text-slate-200 group-hover:text-white mb-1">{title}</h4>
                    <p className="text-xs text-blue-400 flex items-center gap-1 group-hover:underline">
                      {language === "en" ? "Play video" : "Riproduci video"}
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
        <aside className="fixed right-0 top-0 h-full w-full sm:w-96 bg-[#111] border-l border-white/10 z-[60] shadow-2xl transform transition-transform animate-in slide-in-from-right duration-200">
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="h-16 flex items-center justify-between px-6 border-b border-white/5">
              <h3 className="font-semibold">
                {language === "en" ? "Site Details" : "Dettagli Sito"}
              </h3>
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
                    {language === "en" ? "Open Editor" : "Apri Editor"}
                  </Link>
                </div>
              </div>

              {/* Info Block */}
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                    {language === "en" ? "Site Name" : "Nome Sito"}
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <h2 className="text-2xl font-bold">{selectedSite.name}</h2>
                    <button className="p-1 hover:bg-white/10 rounded"><PencilIcon className="w-4 h-4 text-slate-400" /></button>
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                    {language === "en" ? "Domain" : "Dominio"}
                  </label>
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
                  {language === "en" ? "Edit Site" : "Modifica Sito"}
                </Link>
                <button
                  onClick={(e) => handleDeleteSite(selectedSite.id, e)}
                  className="py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  {isDeleting === selectedSite.id ? <div className="w-4 h-4 border-2 border-current rounded-full animate-spin" /> : <TrashIcon className="w-4 h-4" />}
                  {language === "en" ? "Delete" : "Elimina"}
                </button>
                <button className="py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors">
                  <Cog6ToothIcon className="w-4 h-4" />
                  {language === "en" ? "Settings" : "Impostazioni"}
                </button>
              </div>
            </div>
          </div>
        </aside>
      )}

    </div>
  );
}
