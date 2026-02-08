"use client";

import { useEffect, useState } from "react";
import { SparklesIcon } from "@heroicons/react/24/outline";
import { getQuota, UserQuota } from "@/lib/api";

export default function GenerationCounter() {
  const [quota, setQuota] = useState<UserQuota | null>(null);

  useEffect(() => {
    getQuota()
      .then(setQuota)
      .catch(() => {});
  }, []);

  if (!quota) return null;

  const used = quota.generations_used;
  const limit = quota.generations_limit;
  const remaining = quota.remaining_generations;
  const isPremium = quota.is_premium;

  if (isPremium) {
    return (
      <div className="px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
        <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold">
          <SparklesIcon className="w-4 h-4" />
          Premium
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Generazioni illimitate</p>
      </div>
    );
  }

  const percentage = limit > 0 ? (used / limit) * 100 : 0;

  return (
    <div className="px-3 py-2 rounded-lg bg-white/5 border border-white/10">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-slate-400">Generazioni</span>
        <span className="text-xs font-semibold text-white">
          {used}/{limit}
        </span>
      </div>
      <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${
            remaining === 0 ? "bg-red-500" : remaining === 1 ? "bg-amber-500" : "bg-blue-500"
          }`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      {remaining === 0 && (
        <p className="text-[11px] text-red-400 mt-1.5">Limite raggiunto</p>
      )}
    </div>
  );
}
