"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  LockIcon,
  EyeIcon,
  EyeOffIcon,
  AlertCircleIcon,
  CheckCircleIcon,
} from "lucide-react";
import { API_BASE } from "@/lib/api";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  // Redirect to login if no token
  useEffect(() => {
    if (!token) {
      router.replace("/auth");
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 6) {
      setError("La password deve avere almeno 6 caratteri");
      return;
    }

    if (password !== confirmPassword) {
      setError("Le password non corrispondono");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await res.json();

      if (res.ok) {
        setSuccess(true);
        // Redirect to login after 3 seconds
        setTimeout(() => router.push("/auth"), 3000);
      } else {
        setError(data.detail || "Si e' verificato un errore. Il link potrebbe essere scaduto.");
      }
    } catch {
      setError("Errore di connessione. Riprova.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) return null;

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center mb-12">
          <Image
            src="/logo.png"
            alt="E-quipe Logo"
            width={48}
            height={48}
            className="h-12 w-auto"
          />
        </div>

        {success ? (
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-green-500/10 flex items-center justify-center">
              <CheckCircleIcon className="w-8 h-8 text-green-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Password reimpostata!</h2>
            <p className="text-slate-400">
              La tua password e&apos; stata aggiornata con successo.
              Verrai reindirizzato alla pagina di login...
            </p>
            <Link
              href="/auth"
              className="inline-block text-blue-400 hover:underline font-medium"
            >
              Vai al login
            </Link>
          </div>
        ) : (
          <>
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-white mb-2">
                Nuova password
              </h1>
              <p className="text-slate-400">
                Scegli una nuova password per il tuo account
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-red-400 text-sm">
                <AlertCircleIcon className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Nuova password
                </label>
                <div className="relative">
                  <LockIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-12 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                    placeholder="Almeno 6 caratteri"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOffIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Conferma password
                </label>
                <div className="relative">
                  <LockIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    minLength={6}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                    placeholder="Ripeti la password"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl font-semibold text-white hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  "Reimposta password"
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link href="/auth" className="text-slate-400 hover:text-blue-400 transition-colors text-sm">
                Torna al login
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
