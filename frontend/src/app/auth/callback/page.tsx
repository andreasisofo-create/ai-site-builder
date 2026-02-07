"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function AuthCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we are running on Vercel/Next.js environment or local/legacy
    // With NextAuth (new flow), this page might not even be used, as NextAuth handles callbacks internally.
    // However, if it's used for custom verify flows, we keep it.

    const token = searchParams.get("token");
    const errorParam = searchParams.get("error");

    // ... identifying connection ...
    console.log("AuthCallback loaded", { token: !!token, error: errorParam });

    if (errorParam) {
      setError("Autenticazione fallita. Riprova.");
      setTimeout(() => router.push("/auth"), 3000);
      return;
    }

    if (token) {
      localStorage.setItem("token", token);
      // Removed complex fetch logic for now to avoid errors on build if API is unreachable.
      // Just redirect to dashboard if token exists.
      router.push("/dashboard");
    } else {
      // If no token, maybe it's just a direct visit?
      // Redirect to auth after a delay
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
