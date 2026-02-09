"use client";

import { useEffect, useState } from "react";
import {
  SparklesIcon,
  PaintBrushIcon,
  DocumentTextIcon,
  CubeIcon,
  CheckIcon,
} from "@heroicons/react/24/outline";

// Preview data structure from the backend
export interface PreviewData {
  phase: "analyzing" | "theme_complete" | "content_complete" | "complete";
  colors?: {
    primary: string;
    secondary: string;
    accent: string;
    bg: string;
    text: string;
  };
  font_heading?: string;
  font_body?: string;
  sections?: string[];
  hero_title?: string;
  hero_subtitle?: string;
  hero_cta?: string;
  services_titles?: string[];
}

interface GenerationExperienceProps {
  step: number;
  totalSteps: number;
  message: string;
  percentage: number;
  previewData: PreviewData | null;
}

const STEP_CONFIG = [
  { icon: SparklesIcon, label: "Analisi stile e testi", color: "blue" },
  { icon: PaintBrushIcon, label: "Palette e componenti", color: "violet" },
  { icon: DocumentTextIcon, label: "Contenuti e layout", color: "emerald" },
  { icon: CubeIcon, label: "Assemblaggio finale", color: "amber" },
];

export default function GenerationExperience({
  step,
  totalSteps,
  message,
  percentage,
  previewData,
}: GenerationExperienceProps) {
  const [animatedPercentage, setAnimatedPercentage] = useState(0);
  const [showContent, setShowContent] = useState(false);

  // Smooth percentage animation
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedPercentage(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  // Content reveal delay
  useEffect(() => {
    if (previewData) {
      const timer = setTimeout(() => setShowContent(true), 300);
      return () => clearTimeout(timer);
    }
    setShowContent(false);
  }, [previewData?.phase]);

  const phase = previewData?.phase || "analyzing";

  return (
    <div className="w-full space-y-8">
      {/* Main Progress Circle */}
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-32 h-32">
          {/* Background circle */}
          <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60" cy="60" r="52"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="8"
            />
            <circle
              cx="60" cy="60" r="52"
              fill="none"
              stroke="url(#progressGradient)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 52}`}
              strokeDashoffset={`${2 * Math.PI * 52 * (1 - animatedPercentage / 100)}`}
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold">{Math.round(animatedPercentage)}%</span>
            <span className="text-xs text-slate-500">Step {step}/{totalSteps}</span>
          </div>
        </div>

        {/* Status message */}
        <div className="flex items-center gap-2 text-slate-300">
          <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
          <span className="text-sm">{message || "Elaborazione..."}</span>
        </div>
      </div>

      {/* Step indicators */}
      <div className="grid grid-cols-4 gap-2">
        {STEP_CONFIG.map((cfg, idx) => {
          const stepNum = idx + 1;
          const Icon = cfg.icon;
          const isActive = step === stepNum;
          const isDone = step > stepNum;

          return (
            <div
              key={stepNum}
              className={`flex flex-col items-center gap-2 p-3 rounded-xl text-xs transition-all duration-500 ${
                isActive
                  ? "bg-blue-500/10 border border-blue-500/30 text-blue-400"
                  : isDone
                  ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                  : "bg-white/[0.02] border border-white/5 text-slate-600"
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                isActive
                  ? "bg-blue-500/20"
                  : isDone
                  ? "bg-emerald-500/20"
                  : "bg-white/5"
              }`}>
                {isDone ? (
                  <CheckIcon className="w-4 h-4" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span className="text-center leading-tight">{cfg.label}</span>
            </div>
          );
        })}
      </div>

      {/* Progressive Preview Scenes */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden">
        {/* Scene 1: Analyzing (pulsating orb) */}
        {phase === "analyzing" && (
          <div className="p-8 flex flex-col items-center gap-4 animate-in fade-in duration-500">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 animate-pulse" />
              <SparklesIcon className="w-8 h-8 text-blue-400 absolute inset-0 m-auto" />
            </div>
            <p className="text-sm text-slate-400 text-center">
              L&apos;AI sta analizzando il tuo business e creando contenuti unici...
            </p>
          </div>
        )}

        {/* Scene 2: Theme complete - show color palette */}
        {phase === "theme_complete" && previewData?.colors && (
          <div className={`p-6 space-y-4 transition-all duration-700 ${showContent ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <PaintBrushIcon className="w-4 h-4 text-violet-400" />
              Palette colori selezionata
            </h4>
            <div className="flex gap-3">
              {Object.entries(previewData.colors).map(([name, hex]) => (
                <div key={name} className="flex flex-col items-center gap-1.5">
                  <div
                    className="w-12 h-12 rounded-xl shadow-lg transition-transform hover:scale-110"
                    style={{ backgroundColor: hex }}
                  />
                  <span className="text-[10px] text-slate-500 capitalize">{name}</span>
                </div>
              ))}
            </div>
            {previewData.font_heading && (
              <div className="flex items-center gap-4 pt-2 border-t border-white/5">
                <div className="text-xs text-slate-500">
                  Font titoli: <span className="text-slate-300">{previewData.font_heading}</span>
                </div>
                <div className="text-xs text-slate-500">
                  Font corpo: <span className="text-slate-300">{previewData.font_body}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Scene 3: Content complete - show hero preview */}
        {phase === "content_complete" && (
          <div className={`transition-all duration-700 ${showContent ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            {/* Mini preview of the site layout */}
            <div className="p-6 space-y-4">
              <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <DocumentTextIcon className="w-4 h-4 text-emerald-400" />
                Anteprima contenuti
              </h4>

              {/* Hero preview */}
              {previewData?.hero_title && (
                <div
                  className="p-4 rounded-xl border border-white/10"
                  style={{
                    background: previewData?.colors
                      ? `linear-gradient(135deg, ${previewData.colors.primary}15, ${previewData.colors.secondary}15)`
                      : "rgba(255,255,255,0.02)",
                  }}
                >
                  <p className="text-lg font-bold mb-1" style={{
                    color: previewData?.colors?.primary || "#3b82f6"
                  }}>
                    {previewData.hero_title}
                  </p>
                  {previewData.hero_subtitle && (
                    <p className="text-sm text-slate-400 mb-2">{previewData.hero_subtitle}</p>
                  )}
                  {previewData.hero_cta && (
                    <span
                      className="inline-block px-3 py-1 rounded-lg text-xs text-white"
                      style={{ backgroundColor: previewData?.colors?.primary || "#3b82f6" }}
                    >
                      {previewData.hero_cta}
                    </span>
                  )}
                </div>
              )}

              {/* Services preview */}
              {previewData?.services_titles && previewData.services_titles.length > 0 && (
                <div className="grid grid-cols-3 gap-2">
                  {previewData.services_titles.slice(0, 3).map((title, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-white/[0.03] border border-white/5 text-center"
                    >
                      <p className="text-xs text-slate-300 truncate">{title}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Section badges */}
              {previewData?.sections && (
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {previewData.sections.map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded-full bg-white/5 text-[10px] text-slate-500 capitalize"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scene 4: Complete */}
        {phase === "complete" && (
          <div className="p-8 flex flex-col items-center gap-3 animate-in fade-in duration-500">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <CheckIcon className="w-8 h-8 text-emerald-400" />
            </div>
            <p className="text-sm font-medium text-emerald-400">Il tuo sito e&apos; pronto!</p>
            <p className="text-xs text-slate-500">Reindirizzamento all&apos;editor...</p>
          </div>
        )}
      </div>
    </div>
  );
}
