"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  MailIcon,
  LockIcon,
  EyeIcon,
  EyeOffIcon,
  ArrowRightIcon,
  UserIcon,
  AlertCircleIcon
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");

  const { login, register, googleLogin, microsoftLogin } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (isLogin) {
      const result = await login(email, password);

      if (!result.success) {
        setError(result.error || "Errore durante il login");
        setLoading(false);
      } else {
        router.push("/dashboard");
      }
    } else {
      const result = await register(email, password, fullName);

      if (!result.success) {
        setError(result.error || "Errore durante la registrazione");
        setLoading(false);
      } else {
        router.push("/dashboard");
      }
    }
  };

  const handleGoogleLogin = async () => {
    googleLogin();
  };

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Left Side - Form */}
      <div className="flex-1 flex flex-col justify-center items-center px-6 py-12">
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

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              {isLogin ? 'Bentornato' : 'Crea il tuo account'}
            </h1>
            <p className="text-slate-400">
              {isLogin
                ? 'Accedi per continuare a costruire il tuo sito'
                : 'Inizia il tuo viaggio con E-quipe'}
            </p>
          </div>

          {/* Google Login */}
          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-white hover:bg-white/10 transition-colors mb-6"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continua con Google
          </button>

          <button
            onClick={() => microsoftLogin()}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-white hover:bg-white/10 transition-colors mb-6"
          >
            <svg className="w-5 h-5" viewBox="0 0 23 23">
              <path fill="#f35325" d="M1 1h10v10H1z" />
              <path fill="#81bc06" d="M12 1h10v10H12z" />
              <path fill="#05a6f0" d="M1 12h10v10H1z" />
              <path fill="#ffba08" d="M12 12h10v10H12z" />
            </svg>
            Continua con Microsoft
          </button>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-slate-950 text-slate-400">oppure con email</span>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-red-400 text-sm">
              <AlertCircleIcon className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Nome completo
                </label>
                <div className="relative">
                  <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                    placeholder="Mario Rossi"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <div className="relative">
                <MailIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="tu@email.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <LockIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="••••••••"
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

            {!isLogin && (
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  required
                  className="mt-1 rounded border-white/10 bg-white/5 text-blue-500 focus:ring-blue-500"
                />
                <p className="text-sm text-slate-400">
                  Accetto i <Link href="#" className="text-blue-400 hover:underline">Termini di servizio</Link> e la{' '}
                  <Link href="#" className="text-blue-400 hover:underline">Privacy Policy</Link>
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl font-semibold text-white hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isLogin ? 'Accedi' : 'Crea Account'}
                  <ArrowRightIcon className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-slate-400">
            {isLogin ? "Non hai un account?" : "Hai già un account?"}{' '}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-400 hover:underline font-medium"
            >
              {isLogin ? 'Registrati' : 'Accedi'}
            </button>
          </p>

          {/* Back to Home */}
          <div className="mt-8 text-center">
            <Link href="/" className="text-slate-500 hover:text-white transition-colors text-sm">
              ← Torna alla home
            </Link>
          </div>
        </div>
      </div>

      {/* Right Side - Visual */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/50 to-cyan-900/50" />
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1551434678-e076c223a692?w=1200&h=800&fit=crop')] bg-cover bg-center opacity-20" />

        <div className="relative z-10 flex flex-col justify-center items-center p-12 text-center">
          <div className="max-w-md">
            <blockquote className="text-2xl font-medium text-white mb-6">
              &ldquo;E-quipe ha trasformato la nostra presenza online in modo incredibile. Il sito è professionale e perfetto per il nostro business.&rdquo;
            </blockquote>
            <div className="flex items-center justify-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold">
                MR
              </div>
              <div className="text-left">
                <div className="text-white font-medium">Marco Rossi</div>
                <div className="text-slate-400 text-sm">CEO, TechStart Italia</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
