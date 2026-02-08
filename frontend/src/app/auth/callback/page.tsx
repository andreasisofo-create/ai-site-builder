"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

function AuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    const errorParam = searchParams.get("error");

    console.log("AuthCallback loaded", { token: !!token, error: errorParam });

    if (errorParam) {
      setError("Autenticazione fallita. Riprova.");
      setTimeout(() => router.push("/auth"), 3000);
      return;
    }

    if (token) {
      localStorage.setItem("token", token);
      // Fetch user data e salva in localStorage, poi redirect
      (async () => {
        try {
          const res = await fetch("/api/auth/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (res.ok) {
            const userData = await res.json();
            localStorage.setItem("user", JSON.stringify(userData));
          }
        } catch (e) {
          console.error("Errore fetch user dopo OAuth:", e);
        }
        router.push("/dashboard");
      })();
    } else {
      setTimeout(() => router.push("/auth"), 1000);
    }
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="text-center">
        <div className="text-red-400 text-xl mb-4">{error}</div>
        <p className="text-slate-400">Reindirizzamento...</p>
      </div>
    );
  }

  return (
    <div className="text-center">
      <div className="w-12 h-12 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
      <p className="text-slate-400">Completamento autenticazione...</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <Suspense fallback={<div className="text-slate-400">Caricamento...</div>}>
        <AuthCallbackContent />
      </Suspense>
    </div>
  );
}
