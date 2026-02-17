"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function EditorError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Editor error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center text-white">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold mb-2">Errore nell&apos;editor</h2>
        <p className="text-slate-400 text-sm mb-6">
          Si e&apos; verificato un errore nel caricamento dell&apos;editor.
          Prova a ricaricare la pagina.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={reset}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
          >
            Riprova
          </button>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-sm font-medium transition-colors"
          >
            Torna alla dashboard
          </Link>
        </div>
        {process.env.NODE_ENV === "development" && (
          <pre className="mt-6 text-left text-xs text-red-400/80 bg-red-500/10 rounded-lg p-4 overflow-auto max-h-40">
            {error.message}
            {"\n"}
            {error.stack}
          </pre>
        )}
      </div>
    </div>
  );
}
