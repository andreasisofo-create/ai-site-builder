"use client";

export const dynamic = "force-dynamic";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import {
  getServiceCatalog,
  getMySubscriptions,
  ServiceCatalogItem,
  UserSubscription,
} from "@/lib/api";
import { CheckCircleIcon, ShoppingCartIcon } from "@heroicons/react/24/outline";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/sections/Footer";

const CATALOG_FILTER_TABS = (language: string) => [
  { id: "all", label: language === "en" ? "All" : "Tutti" },
  { id: "pack", label: language === "en" ? "Packs" : "Pacchetti" },
  { id: "site", label: language === "en" ? "Website" : "Sito Web" },
  { id: "ads", label: "Ads" },
  { id: "content", label: language === "en" ? "Content" : "Contenuti" },
  {
    id: "hosting_domain",
    label: language === "en" ? "Hosting & Domains" : "Hosting & Domini",
  },
];

export default function PacchettiPage() {
  const { isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const router = useRouter();

  const [catalog, setCatalog] = useState<ServiceCatalogItem[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogFilter, setCatalogFilter] = useState("all");
  const [subscriptions, setSubscriptions] = useState<UserSubscription[]>([]);
  const [checkoutSlug, setCheckoutSlug] = useState<string | null>(null);

  // Load catalog (public, no auth required)
  useEffect(() => {
    loadCatalog();
  }, []);

  // Load subscriptions only if authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadSubscriptions();
    }
  }, [isAuthenticated]);

  const loadCatalog = async () => {
    try {
      setCatalogLoading(true);
      const data = await getServiceCatalog();
      setCatalog(data.services || []);
    } catch (error: any) {
      console.error("Failed to load catalog:", error);
    } finally {
      setCatalogLoading(false);
    }
  };

  const loadSubscriptions = async () => {
    try {
      const data = await getMySubscriptions();
      setSubscriptions(data);
    } catch (error: any) {
      console.error("Failed to load subscriptions:", error);
    }
  };

  const handleChooseService = (slug: string) => {
    setCheckoutSlug(slug);
    if (isAuthenticated) {
      router.push(`/checkout?service=${slug}`);
    } else {
      // Redirect to auth with return URL to checkout
      router.push(
        `/auth?redirect=${encodeURIComponent(`/checkout?service=${slug}`)}`
      );
    }
    // Reset after navigation starts
    setTimeout(() => setCheckoutSlug(null), 500);
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white flex flex-col">
      <Navbar />

      {/* Main Content */}
      <main className="flex-1 pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Header */}
          <section className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              {language === "en" ? "Plans & Services" : "Piani e Servizi"}
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              {language === "en"
                ? "Choose the perfect package for your business"
                : "Scegli il pacchetto perfetto per il tuo business"}
            </p>
          </section>

          {/* Filter Tabs */}
          <div className="flex gap-2 mb-10 overflow-x-auto pb-2 scrollbar-hide justify-center flex-wrap">
            {CATALOG_FILTER_TABS(language).map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCatalogFilter(tab.id)}
                className={`px-5 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  catalogFilter === tab.id
                    ? "bg-white/10 text-white border border-white/20"
                    : "bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white border border-transparent"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Service Cards Grid */}
          {catalogLoading ? (
            <div className="flex items-center justify-center py-24">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : catalog.length === 0 ? (
            <div className="text-center py-24 border border-dashed border-white/10 rounded-2xl bg-white/[0.02]">
              <div className="w-16 h-16 rounded-full bg-white/5 mx-auto flex items-center justify-center mb-4">
                <ShoppingCartIcon className="w-8 h-8 text-slate-500" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">
                {language === "en"
                  ? "No services available"
                  : "Nessun servizio disponibile"}
              </h3>
              <p className="text-slate-500 text-sm">
                {language === "en"
                  ? "Services will be available soon"
                  : "I servizi saranno disponibili a breve"}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {catalog
                .filter((item) => {
                  if (catalogFilter === "all") return true;
                  if (catalogFilter === "hosting_domain")
                    return (
                      item.category === "hosting" ||
                      item.category === "domain"
                    );
                  return item.category === catalogFilter;
                })
                .sort((a, b) => a.display_order - b.display_order)
                .map((item) => {
                  const isPack = item.category === "pack";
                  const name =
                    language === "en" ? item.name_en : item.name;
                  const setupEuros = (item.setup_price_cents / 100).toFixed(
                    item.setup_price_cents % 100 === 0 ? 0 : 2
                  );
                  const monthlyEuros = (
                    item.monthly_price_cents / 100
                  ).toFixed(
                    item.monthly_price_cents % 100 === 0 ? 0 : 2
                  );
                  const hasSetup = item.setup_price_cents > 0;
                  const hasMonthly = item.monthly_price_cents > 0;
                  const isFreeSetup =
                    isPack && item.setup_price_cents === 0;
                  const isOwned = subscriptions.some(
                    (sub) =>
                      sub.service_slug === item.slug &&
                      sub.status === "active"
                  );

                  let features: string[] = [];
                  try {
                    const raw =
                      language === "en"
                        ? item.features_en_json
                        : item.features_json;
                    if (raw) features = JSON.parse(raw);
                  } catch {
                    // ignore parse errors
                  }

                  const displayFeatures = isPack
                    ? features
                    : features.slice(0, 5);
                  const hasMoreFeatures =
                    !isPack && features.length > 5;

                  return (
                    <div
                      key={item.slug}
                      className={`relative bg-[#16162a] rounded-xl p-6 flex flex-col transition-all ${
                        item.is_highlighted
                          ? "border-2 border-blue-500/30 shadow-lg shadow-blue-500/5"
                          : "border border-white/5 hover:border-white/10"
                      } ${isPack ? "md:col-span-1" : ""}`}
                    >
                      {/* Badges */}
                      <div className="flex items-center gap-2 mb-3 flex-wrap">
                        {item.is_highlighted && (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30 uppercase tracking-wider">
                            {language === "en"
                              ? "RECOMMENDED"
                              : "CONSIGLIATO"}
                          </span>
                        )}
                        {isFreeSetup && (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                            {language === "en"
                              ? "FREE SETUP"
                              : "SETUP GRATUITO"}
                          </span>
                        )}
                        {isOwned && (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                            <CheckCircleIcon className="w-3.5 h-3.5" />
                            {language === "en" ? "Active" : "Attivo"}
                          </span>
                        )}
                      </div>

                      {/* Service Name */}
                      <h4 className="font-semibold text-white text-lg mb-3">
                        {name}
                      </h4>

                      {/* Pricing */}
                      <div className="mb-4 space-y-1">
                        {hasSetup && (
                          <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-white">
                              {"\u20AC"}
                              {setupEuros}
                            </span>
                            <span className="text-sm text-slate-400">
                              {language === "en"
                                ? "one-time"
                                : "una tantum"}
                            </span>
                          </div>
                        )}
                        {hasMonthly && (
                          <div className="flex items-baseline gap-2">
                            {!hasSetup && (
                              <span className="text-2xl font-bold text-white">
                                {"\u20AC"}
                                {monthlyEuros}
                              </span>
                            )}
                            {hasSetup && (
                              <span className="text-sm text-slate-300">
                                + {"\u20AC"}
                                {monthlyEuros}
                              </span>
                            )}
                            <span className="text-sm text-slate-400">
                              {language === "en" ? "/month" : "/mese"}
                            </span>
                          </div>
                        )}
                        {!hasSetup && !hasMonthly && (
                          <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-white">
                              {language === "en" ? "Free" : "Gratuito"}
                            </span>
                          </div>
                        )}
                        {!hasMonthly && hasSetup && (
                          <div className="text-sm text-slate-400">
                            {language === "en"
                              ? "One-time"
                              : "Una tantum"}
                          </div>
                        )}
                      </div>

                      {/* Features List */}
                      {displayFeatures.length > 0 && (
                        <ul className="space-y-2 mb-5 flex-1">
                          {displayFeatures.map((feat, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-sm text-slate-400"
                            >
                              <CheckCircleIcon className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                              <span>{feat}</span>
                            </li>
                          ))}
                          {hasMoreFeatures && (
                            <li className="text-xs text-slate-500 pl-6">
                              +{features.length - 5}{" "}
                              {language === "en" ? "more..." : "altro..."}
                            </li>
                          )}
                        </ul>
                      )}

                      {/* CTA Button */}
                      {!isOwned ? (
                        <button
                          onClick={() => handleChooseService(item.slug)}
                          disabled={checkoutSlug !== null}
                          className={`mt-auto w-full py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-50 ${
                            item.is_highlighted
                              ? "bg-[#0090FF] hover:bg-[#0070C9] text-white"
                              : "bg-white/10 hover:bg-white/15 text-white border border-white/10"
                          }`}
                        >
                          {checkoutSlug === item.slug ? (
                            <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                          ) : null}
                          {language === "en" ? "Choose" : "Scegli"}
                        </button>
                      ) : (
                        <Link
                          href="/dashboard#section-servizi"
                          className="mt-auto w-full py-2.5 rounded-lg text-sm font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-center flex items-center justify-center gap-2 hover:bg-emerald-500/20 transition-colors"
                        >
                          <CheckCircleIcon className="w-4 h-4" />
                          {language === "en" ? "Manage" : "Gestisci"}
                        </Link>
                      )}
                    </div>
                  );
                })}
            </div>
          )}

          {/* Bottom Notes */}
          <div className="mt-12 text-center space-y-2">
            <p className="text-sm text-slate-500">
              {language === "en"
                ? "* Ad budget excluded"
                : "* Budget pubblicitario esclusi"}
            </p>
            <p className="text-sm text-slate-500">
              {language === "en"
                ? "** 15% discount for annual payment"
                : "** Sconto 15% pagamento annuale"}
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
