"use client";

export const dynamic = "force-dynamic";

import { Suspense, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, Lock, CheckCircle, Loader2, AlertCircle, Star } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import {
  getServiceCatalog,
  getMySubscriptions,
  checkoutService,
  ServiceCatalogItem,
} from "@/lib/api";

// ==================== HELPERS ====================

/** Convert cents to EUR string, e.g. 49900 -> "499" */
function formatPrice(cents: number): string {
  const euros = cents / 100;
  return euros % 1 === 0 ? euros.toFixed(0) : euros.toFixed(2);
}

// ==================== MAIN PAGE (Suspense wrapper) ====================

export default function CheckoutPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <CheckoutContent />
    </Suspense>
  );
}

// ==================== CHECKOUT CONTENT ====================

function CheckoutContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { language, t } = useLanguage();

  const serviceSlug = searchParams.get("service") || "";

  const [catalog, setCatalog] = useState<ServiceCatalogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [alreadyOwned, setAlreadyOwned] = useState(false);

  // ---- Fetch catalog (PUBLIC, no auth needed) ----
  const fetchCatalog = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getServiceCatalog();
      setCatalog(data.services);

      // Check if user already has this service active
      if (isAuthenticated && serviceSlug) {
        try {
          const subs = await getMySubscriptions();
          const hasActive = subs.some(
            (sub) => sub.service_slug === serviceSlug && sub.status === "active"
          );
          setAlreadyOwned(hasActive);
        } catch {
          // Ignore - subscription check is best-effort
        }
      }
    } catch (err: any) {
      setError(err.message || t("checkout.loadingError"));
    } finally {
      setLoading(false);
    }
  }, [t, isAuthenticated, serviceSlug]);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  // ---- Find service ----
  const service = catalog.find((s) => s.slug === serviceSlug);

  // ---- Parse features ----
  const features: string[] = (() => {
    if (!service) return [];
    const raw =
      language === "en" ? service.features_en_json : service.features_json;
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  })();

  // ---- Pricing logic ----
  const hasSetup = service ? service.setup_price_cents > 0 : false;
  const hasMonthly = service ? service.monthly_price_cents > 0 : false;
  const firstPaymentCents = service
    ? hasSetup
      ? service.setup_price_cents
      : service.monthly_price_cents
    : 0;

  // ---- Service display name ----
  const serviceName = service
    ? language === "en"
      ? service.name_en
      : service.name
    : "";

  // ---- Checkout handler: check auth ONLY here ----
  const handleCheckout = async () => {
    if (!service) return;

    // Se gia' attivo, blocca
    if (alreadyOwned) {
      toast.error(
        language === "en"
          ? "You already have this service active."
          : "Hai gia' questo servizio attivo."
      );
      return;
    }

    // Se non autenticato, manda al login e poi ritorna qui
    if (!isAuthenticated) {
      router.push(
        `/auth?redirect=${encodeURIComponent(`/checkout?service=${serviceSlug}`)}`
      );
      return;
    }

    setCheckoutLoading(true);
    try {
      const result = await checkoutService(service.slug);
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      } else if (result.activated) {
        toast.success(
          language === "en"
            ? "Service activated successfully!"
            : "Servizio attivato con successo!"
        );
        router.push(`/dashboard?payment=success&service=${service.slug}`);
      } else {
        toast.success(
          language === "en"
            ? "Order created. Complete the payment."
            : "Ordine creato. Completa il pagamento."
        );
      }
    } catch (err: any) {
      if ((err as any).status === 401) {
        toast.error(
          language === "en"
            ? "Session expired. Please log in again."
            : "Sessione scaduta. Effettua nuovamente il login."
        );
        router.push(
          `/auth?redirect=${encodeURIComponent(`/checkout?service=${serviceSlug}`)}`
        );
      } else if ((err as any).status === 409) {
        toast.error(
          language === "en"
            ? "You already have an active subscription for this service."
            : "Hai gia' un abbonamento attivo per questo servizio."
        );
        setAlreadyOwned(true);
      } else {
        toast.error(err.message || t("checkout.checkoutError"));
      }
    } finally {
      setCheckoutLoading(false);
    }
  };

  // ---- Loading state ----
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // ---- Error state ----
  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">
            {t("checkout.loadingError")}
          </h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchCatalog}
            className="px-6 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-semibold transition-colors"
          >
            {language === "en" ? "Try again" : "Riprova"}
          </button>
        </div>
      </div>
    );
  }

  // ---- Service not found ----
  if (!loading && !service) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">
            {t("checkout.serviceNotFound")}
          </h2>
          <p className="text-gray-400 mb-6">
            {t("checkout.serviceNotFoundDesc")}
          </p>
          <Link
            href="/pacchetti"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#0090FF] hover:bg-[#0070C9] text-white rounded-xl font-semibold transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            {t("checkout.backToPricing")}
          </Link>
        </div>
      </div>
    );
  }

  // ---- Main checkout view ----
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="max-w-lg mx-auto px-4 py-12 sm:py-20">
        {/* Back link */}
        <Link
          href="/pacchetti"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          {t("checkout.back")}
        </Link>

        {/* Title */}
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-8">
          {t("checkout.title")}
        </h1>

        {/* Card */}
        <div className="bg-[#161616] border border-white/10 rounded-2xl p-6 sm:p-8 mb-8">
          {/* Service name + badges */}
          <div className="flex items-start justify-between mb-1">
            <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
              {serviceName}
              {service?.is_highlighted && (
                <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
              )}
            </h2>
          </div>
          {service?.is_highlighted && (
            <span className="inline-block text-xs font-bold text-[#0090FF] bg-[#0090FF]/10 px-2 py-0.5 rounded-full mb-4">
              {t("checkout.recommended")}
            </span>
          )}
          {!service?.is_highlighted && hasSetup && service.setup_price_cents === 0 && (
            <span className="inline-block text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full mb-4">
              {t("checkout.freeSetup")}
            </span>
          )}

          {/* Pricing breakdown */}
          <div className="space-y-3 mt-4">
            {hasSetup && service.setup_price_cents > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">{t("checkout.setupFee")}</span>
                <span className="text-white font-semibold">
                  &euro;{formatPrice(service.setup_price_cents)}
                </span>
              </div>
            )}
            {hasSetup && service.setup_price_cents === 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">{t("checkout.setupFee")}</span>
                <span className="text-emerald-400 font-semibold">
                  {language === "en" ? "Free" : "Gratuito"}
                </span>
              </div>
            )}
            {hasMonthly && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">{t("checkout.monthlyFee")}</span>
                <span className="text-white font-semibold">
                  &euro;{formatPrice(service.monthly_price_cents)}
                  <span className="text-gray-500 font-normal">
                    /{language === "en" ? "mo" : "mese"}
                  </span>
                </span>
              </div>
            )}

            {/* Divider */}
            <div className="border-t border-white/10 pt-3 mt-3">
              {firstPaymentCents > 0 ? (
                <>
                  <div className="flex justify-between">
                    <span className="text-white font-semibold">
                      {t("checkout.firstPayment")}
                    </span>
                    <span className="text-white text-lg font-bold">
                      &euro;{formatPrice(firstPaymentCents)}
                    </span>
                  </div>
                  {hasSetup && hasMonthly && (
                    <p className="text-gray-500 text-xs mt-1 text-right">
                      {t("checkout.thenMonthly").replace(
                        "{price}",
                        `\u20AC${formatPrice(service.monthly_price_cents)}`
                      )}
                    </p>
                  )}
                </>
              ) : (
                <div className="flex justify-between items-center">
                  <span className="text-white font-semibold">
                    {t("checkout.immediateActivation")}
                  </span>
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                </div>
              )}
            </div>
          </div>

          {/* Features */}
          {features.length > 0 && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">
                {t("checkout.features")}
              </h3>
              <ul className="space-y-2">
                {features.map((feature, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-300"
                  >
                    <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* CTA Button */}
        {alreadyOwned ? (
          <div className="w-full flex items-center justify-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-xl font-bold py-4 text-base sm:text-lg">
            <CheckCircle className="w-5 h-5" />
            {language === "en" ? "Already active" : "Gia' attivo"}
          </div>
        ) : (
          <button
            onClick={handleCheckout}
            disabled={checkoutLoading}
            className="w-full flex items-center justify-center gap-2 bg-[#0090FF] hover:bg-[#0070C9] disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-xl font-bold py-4 text-base sm:text-lg transition-colors"
          >
            {checkoutLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {t("checkout.processing")}
              </>
            ) : !isAuthenticated ? (
              <>
                <Lock className="w-4 h-4" />
                {language === "en" ? "Log in to proceed" : "Accedi per procedere"}
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                {t("checkout.proceed")}
              </>
            )}
          </button>
        )}

        {/* Secure payment note */}
        <p className="text-center text-gray-500 text-xs mt-3 flex items-center justify-center gap-1.5">
          <Lock className="w-3 h-3" />
          {t("checkout.securePayment")}
        </p>
      </div>
    </div>
  );
}
