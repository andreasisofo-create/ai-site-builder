"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeftIcon, EyeIcon, PaperAirplaneIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface Site {
  id: number;
  name: string;
  slug: string;
  config: object;
}

interface Component {
  id: number;
  name: string;
  type: string;
  content: object;
  styles: object;
  order: number;
}

export default function Editor() {
  const params = useParams();
  const siteId = params.id as string;
  
  const [site, setSite] = useState<Site | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (siteId) {
      fetchSite();
      fetchComponents();
    }
  }, [siteId]);

  const fetchSite = async () => {
    try {
      const res = await fetch(`/api/sites/${siteId}`);
      if (res.ok) {
        const data = await res.json();
        setSite(data);
      }
    } catch (error) {
      toast.error("Errore nel caricamento sito");
    } finally {
      setLoading(false);
    }
  };

  const fetchComponents = async () => {
    try {
      const res = await fetch(`/api/components/site/${siteId}`);
      if (res.ok) {
        const data = await res.json();
        setComponents(data);
      }
    } catch (error) {
      console.error("Errore caricamento componenti");
    }
  };

  const addComponent = async (type: string) => {
    const name = prompt("Nome del componente:", `Nuovo ${type}`);
    if (!name) return;

    try {
      const res = await fetch("/api/components/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          site_id: siteId,
          name,
          type,
          content: JSON.stringify({}),
        }),
      });

      if (res.ok) {
        toast.success("Componente aggiunto");
        fetchComponents();
      }
    } catch (error) {
      toast.error("Errore nell'aggiunta");
    }
  };

  if (loading) return <div className="p-8">Caricamento...</div>;
  if (!site) return <div className="p-8">Sito non trovato</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="btn-secondary">
              <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="font-semibold">{site.name}</h1>
              <p className="text-sm text-gray-500">/{site.slug}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button className="btn-secondary flex items-center gap-2">
              <EyeIcon className="w-4 h-4" />
              Anteprima
            </button>
            <button className="btn-primary flex items-center gap-2">
              <PaperAirplaneIcon className="w-4 h-4" />
              Pubblica
            </button>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-64px)]">
        {/* Sidebar - Componenti */}
        <aside className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h2 className="font-medium mb-4">Componenti</h2>
            <div className="space-y-2">
              <ComponentButton label="Hero" onClick={() => addComponent("hero")} />
              <ComponentButton label="Testo" onClick={() => addComponent("text")} />
              <ComponentButton label="Immagine" onClick={() => addComponent("image")} />
              <ComponentButton label="Features" onClick={() => addComponent("features")} />
              <ComponentButton label="Pricing" onClick={() => addComponent("pricing")} />
              <ComponentButton label="FAQ" onClick={() => addComponent("faq")} />
              <ComponentButton label="Contatti" onClick={() => addComponent("contact")} />
              <ComponentButton label="Footer" onClick={() => addComponent("footer")} />
            </div>
          </div>
        </aside>

        {/* Canvas */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto bg-white min-h-[800px] rounded-lg shadow-sm">
            {components.length === 0 ? (
              <div className="flex items-center justify-center h-96 text-gray-400">
                <div className="text-center">
                  <p className="mb-2">Nessun componente</p>
                  <p className="text-sm">Aggiungi componenti dalla sidebar</p>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {components.map((comp) => (
                  <div key={comp.id} className="p-6 hover:bg-gray-50 cursor-pointer">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{comp.name}</span>
                      <span className="text-xs text-gray-500 uppercase">{comp.type}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>

        {/* Properties Panel */}
        <aside className="w-72 bg-white border-l border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h2 className="font-medium mb-4">Proprietà</h2>
            <p className="text-sm text-gray-500">
              Seleziona un componente per modificarlo
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

function ComponentButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors text-sm"
    >
      {label}
    </button>
  );
}
