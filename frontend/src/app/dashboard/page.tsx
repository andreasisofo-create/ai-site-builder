"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PlusIcon, GlobeAltIcon, PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface Site {
  id: number;
  name: string;
  slug: string;
  is_published: boolean;
  created_at: string;
}

export default function Dashboard() {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    try {
      const res = await fetch("/api/sites/");
      if (res.ok) {
        const data = await res.json();
        setSites(data);
      }
    } catch (error) {
      toast.error("Errore nel caricamento siti");
    } finally {
      setLoading(false);
    }
  };

  const createSite = async () => {
    const name = prompt("Nome del sito:");
    if (!name) return;
    
    const slug = prompt("Slug (URL-friendly):", name.toLowerCase().replace(/\s+/g, "-"));
    if (!slug) return;

    try {
      const res = await fetch("/api/sites/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ name, slug }),
      });

      if (res.ok) {
        toast.success("Sito creato!");
        fetchSites();
      } else {
        toast.error("Errore nella creazione");
      }
    } catch (error) {
      toast.error("Errore di connessione");
    }
  };

  const deleteSite = async (id: number) => {
    if (!confirm("Sei sicuro di voler eliminare questo sito?")) return;

    try {
      const res = await fetch(`/api/sites/${id}`, { method: "DELETE" });
      if (res.ok) {
        toast.success("Sito eliminato");
        fetchSites();
      }
    } catch (error) {
      toast.error("Errore nell'eliminazione");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <button onClick={createSite} className="btn-primary flex items-center gap-2">
            <PlusIcon className="w-5 h-5" />
            Nuovo Sito
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-12">Caricamento...</div>
        ) : sites.length === 0 ? (
          <div className="card text-center py-12">
            <GlobeAltIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Nessun sito</h3>
            <p className="text-gray-600 mb-4">Crea il tuo primo sito per iniziare</p>
            <button onClick={createSite} className="btn-primary">
              Crea Sito
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sites.map((site) => (
              <div key={site.id} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{site.name}</h3>
                    <p className="text-sm text-gray-500">/{site.slug}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      site.is_published
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {site.is_published ? "Pubblicato" : "Bozza"}
                  </span>
                </div>

                <div className="flex gap-2">
                  <Link
                    href={`/editor/${site.id}`}
                    className="btn-secondary flex-1 flex items-center justify-center gap-1"
                  >
                    <PencilIcon className="w-4 h-4" />
                    Modifica
                  </Link>
                  <button
                    onClick={() => deleteSite(site.id)}
                    className="btn bg-red-100 text-red-700 hover:bg-red-200"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
