"use client";

import { useEffect, useState } from "react";
import { SparklesIcon, CrownIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import { getQuota, upgradeToPremium, UserQuota } from "@/lib/api";
import toast from "react-hot-toast";

export default function GenerationCounter() {
  const [quota, setQuota] = useState<UserQuota | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUpgrading, setIsUpgrading] = useState(false);

  useEffect(() => {
    loadQuota();
  }, []);

  const loadQuota = async () => {
    try {
      const data = await getQuota();
      setQuota(data);
    } catch (error) {
      console.error("Errore caricamento quota:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      setIsUpgrading(true);
      const result = await upgradeToPremium();
      toast.success(result.message);
      loadQuota(); // Ricarica quota aggiornata
    } catch (error: any) {
      toast.error(error.message || "Errore nell'upgrade");
    } finally {
      setIsUpgrading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 animate-pulse">
        <div className="h-4 bg-white/10 rounded w-24" />
      </div>
    );
  }

  if (!quota) return null;

  // Utente Premium
  if (quota.is_premium) {
    return (
      <div className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
            <CrownIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-amber-400">Piano Premium</p>
            <p className="text-xs text-slate-400">Generazioni illimitate</p>
          </div>
        </div>
      </div>
    );
  }

  // Utente Free
  const isLimitReached = quota.remaining_generations === 0;
  const progressPercent = (quota.generations_used / quota.generations_limit) * 100;

  return (
    <div className={`p-4 rounded-xl border ${
      isLimitReached 
        ? "bg-red-500/5 border-red-500/20" 
        : "bg-white/[0.02] border-white/5"
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            isLimitReached 
              ? "bg-red-500/20" 
              : "bg-blue-500/20"
          }`}>
            {isLimitReached ? (
              <LockClosedIcon className="w-5 h-5 text-red-400" />
            ) : (
              <SparklesIcon className="w-5 h-5 text-blue-400" />
            )}
          </div>
          <div>
            <p className={`font-medium ${isLimitReached ? "text-red-400" : "text-white"}`}>
              {isLimitReached ? "Limite raggiunto" : "Piano Free"}
            </p>
            <p className="text-xs text-slate-400">
              {quota.generations_used} di {quota.generations_limit} generazioni usate
            </p>
          </div>
        </div>
        
        {!isLimitReached && (
          <span className="text-2xl font-bold text-white">
            {quota.remaining_generations}
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-white/5 rounded-full overflow-hidden mb-3">
        <div 
          className={`h-full rounded-full transition-all ${
            isLimitReached 
              ? "bg-red-500" 
              : progressPercent > 50 
                ? "bg-amber-500" 
                : "bg-blue-500"
          }`}
          style={{ width: `${Math.min(progressPercent, 100)}%` }}
        />
      </div>

      {/* CTA Upgrade */}
      {isLimitReached ? (
        <button
          onClick={handleUpgrade}
          disabled={isUpgrading}
          className="w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2"
        >
          {isUpgrading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Attivazione...
            </>
          ) : (
            <>
              <CrownIcon className="w-4 h-4" />
              Attiva Generazioni Illimitate
            </>
          )}
        </button>
      ) : (
        <button
          onClick={handleUpgrade}
          disabled={isUpgrading}
          className="w-full py-2 text-sm text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all"
        >
          Aggiorna a Premium per illimitate
        </button>
      )}
      
      <p className="text-xs text-slate-500 text-center mt-2">
        DEMO: Clicca per attivare gratis
      </p>
    </div>
  );
}
