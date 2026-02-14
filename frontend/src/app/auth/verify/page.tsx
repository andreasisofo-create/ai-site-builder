"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";
import { API_BASE } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const { language } = useLanguage();

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage(language === "en" ? "Verification token missing." : "Token di verifica mancante.");
      return;
    }

    const verify = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/verify-email?token=${token}`);
        const data = await res.json();

        if (res.ok) {
          setStatus("success");
          setMessage(data.message || (language === "en" ? "Email verified successfully!" : "Email verificata con successo!"));
          setTimeout(() => router.push("/dashboard"), 3000);
        } else {
          setStatus("error");
          setMessage(data.detail || (language === "en" ? "Invalid or expired token." : "Token non valido o scaduto."));
        }
      } catch {
        setStatus("error");
        setMessage(language === "en" ? "Connection error. Please try again." : "Errore di connessione. Riprova.");
      }
    };

    verify();
  }, [token, router, language]);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center space-y-6">
        {status === "loading" && (
          <>
            <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
            <h1 className="text-2xl font-bold">
              {language === "en" ? "Verifying..." : "Verifica in corso..."}
            </h1>
            <p className="text-slate-400">
              {language === "en" ? "We are verifying your email" : "Stiamo verificando la tua email"}
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto">
              <CheckCircleIcon className="w-10 h-10 text-emerald-400" />
            </div>
            <h1 className="text-2xl font-bold">
              {language === "en" ? "Email Verified!" : "Email Verificata!"}
            </h1>
            <p className="text-slate-400">{message}</p>
            <p className="text-sm text-slate-500">
              {language === "en" ? "Redirecting to dashboard in 3 seconds..." : "Redirect alla dashboard in 3 secondi..."}
            </p>
            <Link
              href="/dashboard"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-medium transition-colors"
            >
              {language === "en" ? "Go to Dashboard" : "Vai alla Dashboard"}
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto">
              <XCircleIcon className="w-10 h-10 text-red-400" />
            </div>
            <h1 className="text-2xl font-bold">
              {language === "en" ? "Verification Failed" : "Verifica Fallita"}
            </h1>
            <p className="text-slate-400">{message}</p>
            <Link
              href="/auth"
              className="inline-block px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-medium transition-colors"
            >
              {language === "en" ? "Back to Login" : "Torna al Login"}
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center px-4">
          <div className="max-w-md w-full text-center space-y-6">
            <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
            <h1 className="text-2xl font-bold">Loading...</h1>
          </div>
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
