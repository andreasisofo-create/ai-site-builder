"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AuthCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    const errorParam = searchParams.get("error");

    if (errorParam) {
      setError("Autenticazione fallita. Riprova.");
      setTimeout(() => {
        router.push("/auth");
      }, 3000);
      return;
    }

    if (token) {
      // Store token and fetch user data
      localStorage.setItem("token", token);
      
      // Fetch user info
      fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch user");
          return res.json();
        })
        .then((user) => {
          localStorage.setItem("user", JSON.stringify(user));
          router.push("/dashboard");
        })
        .catch((err) => {
          console.error("Error fetching user:", err);
          setError("Errore durante il recupero dei dati utente");
          setTimeout(() => {
            router.push("/auth");
          }, 3000);
        });
    } else {
      setError("Token mancante");
      setTimeout(() => {
        router.push("/auth");
      }, 3000);
    }
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">{error}</div>
          <p className="text-slate-400">Reindirizzamento alla pagina di login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-400">Completamento autenticazione...</p>
      </div>
    </div>
  );
}
