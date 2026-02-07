"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeftIcon,
  EyeIcon,
  PaperAirplaneIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { getSite, getSitePreview, updateSite, Site } from "@/lib/api";

export default function Editor() {
  const params = useParams();
  const router = useRouter();
  const siteId = params.id as string;

  const [site, setSite] = useState<Site | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewMode, setPreviewMode] = useState<"desktop" | "mobile">("desktop");
  const [isPublishing, setIsPublishing] = useState(false);

  useEffect(() => {
    if (siteId) {
      loadSite();
    }
  }, [siteId]);

  const loadSite = async () => {
    try {
      setLoading(true);
      const data = await getSite(Number(siteId));
      setSite(data);
    } catch (error: any) {
      toast.error(error.message || "Errore nel caricamento sito");
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!site) return;

    try {
      setIsPublishing(true);
      await updateSite(site.id, {
        is_published: true,
        status: "published",
      });
      toast.success("Sito pubblicato con successo!");
      loadSite(); // Ricarica per aggiornare stato
    } catch (error: any) {
      toast.error(error.message || "Errore nella pubblicazione");
    } finally {
      setIsPublishing(false);
    }
  };

  const getStatusBadge = () => {
    if (!site) return null;

    switch (site.status) {
      case "published":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/20 text-emerald-400 text-sm">
            <CheckCircleIcon className="w-4 h-4" />
            Online
          </span>
        );
      case "ready":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-400 text-sm">
            <SparklesIcon className="w-4 h-4" />
            Pronto
          </span>
        );
      case "generating":
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-400 text-sm">
            <ArrowPathIcon className="w-4 h-4 animate-spin" />
            Generazione...
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-500/20 text-slate-400 text-sm">
            <ExclamationCircleIcon className="w-4 h-4" />
            Bozza
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!site) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white">
        <div className="text-center">
          <p className="text-slate-400">Sito non trovato</p>
          <Link href="/dashboard" className="text-blue-500 hover:underline mt-2 inline-block">
            Torna alla dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col">
      {/* Header */}
      <header className="h-16 bg-[#111] border-b border-white/5 sticky top-0 z-50">
        <div className="h-full px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-semibold">{site.name}</h1>
              <p className="text-sm text-slate-400">{site.slug}.e-quipe.app</p>
            </div>
            <div className="hidden sm:flex items-center gap-2 ml-4">
              {getStatusBadge()}
            </div>
          </div>

          {/* Center: Preview Controls */}
          <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setPreviewMode("desktop")}
              className={`p-2 rounded-md transition-all ${previewMode === "desktop"
                ? "bg-white/10 text-white"
                : "text-slate-400 hover:text-white"
                }`}
              title="Desktop view"
            >
              <ComputerDesktopIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setPreviewMode("mobile")}
              className={`p-2 rounded-md transition-all ${previewMode === "mobile"
                ? "bg-white/10 text-white"
                : "text-slate-400 hover:text-white"
                }`}
              title="Mobile view"
            >
              <DevicePhoneMobileIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            {site.is_published ? (
              <a
                href={`https://${site.slug}.e-quipe.app`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
              >
                <EyeIcon className="w-4 h-4" />
                Visita
              </a>
            ) : (
              <button
                onClick={handlePublish}
                disabled={isPublishing || site.status !== "ready"}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-all"
              >
                {isPublishing ? (
                  <>
                    <ArrowPathIcon className="w-4 h-4 animate-spin" />
                    Pubblicazione...
                  </>
                ) : (
                  <>
                    <PaperAirplaneIcon className="w-4 h-4" />
                    Pubblica
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Preview */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Tools */}
        <aside className="w-64 bg-[#111] border-r border-white/5 overflow-y-auto hidden lg:block">
          <div className="p-4 space-y-6">
            {/* Info Site */}
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-3">Info Sito</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Stato</span>
                  <span className="capitalize">{site.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Creato</span>
                  <span>{new Date(site.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Slug</span>
                  <span className="text-slate-400">{site.slug}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-white/5">
              <h3 className="text-sm font-medium text-slate-400 mb-3">Azioni</h3>
              <div className="space-y-2">
                <Link
                  href={`/dashboard/new`}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all"
                >
                  <SparklesIcon className="w-4 h-4" />
                  Rigenera con AI
                </Link>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/preview/${site.slug}`);
                    toast.success("Link copiato!");
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all text-left"
                >
                  <EyeIcon className="w-4 h-4" />
                  Copia link preview
                </button>
              </div>
            </div>
          </div>
        </aside>

        {/* Center - Preview Iframe */}
        <div className="flex-1 bg-[#0a0a0a] relative overflow-hidden flex items-center justify-center p-8">
          {/* Grid Background */}
          <div
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px'
            }}
          />

          {/* Iframe Container */}
          <div
            className={`relative bg-white rounded-lg shadow-2xl overflow-hidden transition-all duration-300 ${previewMode === "mobile"
              ? "w-[375px] h-[812px]"
              : "w-full max-w-6xl h-full max-h-[calc(100vh-120px)]"
              }`}
          >
            {site.html_content ? (
              <iframe
                srcDoc={site.html_content}
                className="w-full h-full border-0"
                sandbox="allow-scripts"
                title={`Preview - ${site.name}`}
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 bg-slate-900">
                <SparklesIcon className="w-12 h-12 mb-4 opacity-50" />
                <p className="text-lg font-medium">Nessun contenuto generato</p>
                <p className="text-sm opacity-70 mt-1">
                  Il sito non è stato ancora generato dall&apos;AI
                </p>
                <Link
                  href="/dashboard/new"
                  className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-sm transition-colors"
                >
                  Crea nuovo sito
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
