"use client";

import { useState, useCallback } from "react";
import {
  SparklesIcon,
  PhotoIcon,
  CheckIcon,
  XMarkIcon,
  ChevronRightIcon,
  ArrowRightIcon,
} from "@heroicons/react/24/outline";
import type { SitePlanQuestion } from "@/lib/api";

interface PreGenerationQuestionsProps {
  questions: SitePlanQuestion[];
  plan: Record<string, any>;
  onSubmit: (answers: Record<string, any>) => void;
  onSkipAll: () => void;
  language?: string;
}

// Group questions by section
function groupBySection(questions: SitePlanQuestion[]): Record<string, SitePlanQuestion[]> {
  const groups: Record<string, SitePlanQuestion[]> = {};
  for (const q of questions) {
    const key = q.section || "general";
    if (!groups[key]) groups[key] = [];
    groups[key].push(q);
  }
  return groups;
}

const SECTION_LABELS_IT: Record<string, string> = {
  hero: "Hero",
  about: "Chi Siamo",
  services: "Servizi",
  gallery: "Galleria",
  contact: "Contatti",
  testimonials: "Testimonianze",
  team: "Team",
  pricing: "Prezzi",
  faq: "FAQ",
  footer: "Footer",
  general: "Informazioni Generali",
  stats: "Statistiche",
  cta: "Call to Action",
};

export default function PreGenerationQuestions({
  questions,
  plan,
  onSubmit,
  onSkipAll,
  language = "it",
}: PreGenerationQuestionsProps) {
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);

  const grouped = groupBySection(questions);
  const sectionKeys = Object.keys(grouped);
  const totalSections = sectionKeys.length;

  const currentSection = sectionKeys[currentSectionIndex] || "";
  const currentQuestions = grouped[currentSection] || [];

  const setAnswer = useCallback((questionId: string, value: any) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  }, []);

  const handleNext = () => {
    if (currentSectionIndex < totalSections - 1) {
      setCurrentSectionIndex(prev => prev + 1);
    } else {
      onSubmit(answers);
    }
  };

  const handlePrev = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
    }
  };

  const isLastSection = currentSectionIndex === totalSections - 1;
  const answeredCount = Object.keys(answers).length;
  const progress = totalSections > 0 ? ((currentSectionIndex + 1) / totalSections) * 100 : 0;

  if (questions.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm">
          <SparklesIcon className="w-4 h-4" />
          {language === "en"
            ? "Personalize your site"
            : "Personalizza il tuo sito"}
        </div>
        <h2 className="text-xl font-semibold text-white">
          {language === "en"
            ? "A few quick questions"
            : "Qualche domanda veloce"}
        </h2>
        <p className="text-sm text-slate-400">
          {language === "en"
            ? "Answer to personalize, or skip and let AI handle it"
            : "Rispondi per personalizzare, oppure salta e lascia fare all'AI"}
        </p>
      </div>

      {/* Progress bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-slate-500">
          <span>
            {SECTION_LABELS_IT[currentSection] || currentSection}
          </span>
          <span>{currentSectionIndex + 1} / {totalSections}</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Questions for current section */}
      <div className="space-y-4">
        {currentQuestions.map((q) => (
          <QuestionCard
            key={q.id}
            question={q}
            value={answers[q.id]}
            onChange={(val) => setAnswer(q.id, val)}
            language={language}
          />
        ))}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={handlePrev}
          disabled={currentSectionIndex === 0}
          className="px-4 py-2 text-sm text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          {language === "en" ? "Back" : "Indietro"}
        </button>

        <button
          onClick={onSkipAll}
          className="px-4 py-2 text-sm text-slate-500 hover:text-slate-300 transition-colors"
        >
          {language === "en" ? "Skip all, let AI decide" : "Salta tutto, decide l'AI"}
        </button>

        <button
          onClick={handleNext}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl text-sm font-medium hover:opacity-90 transition-all text-white"
        >
          {isLastSection
            ? (language === "en" ? "Generate" : "Genera")
            : (language === "en" ? "Next" : "Avanti")}
          {isLastSection ? (
            <SparklesIcon className="w-4 h-4" />
          ) : (
            <ArrowRightIcon className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Summary */}
      {answeredCount > 0 && (
        <p className="text-center text-xs text-slate-500">
          {language === "en"
            ? `${answeredCount} answer(s) provided`
            : `${answeredCount} risposta/e fornita/e`}
        </p>
      )}
    </div>
  );
}

// Individual question card
function QuestionCard({
  question,
  value,
  onChange,
  language,
}: {
  question: SitePlanQuestion;
  value: any;
  onChange: (val: any) => void;
  language: string;
}) {
  const isAnswered = value !== undefined && value !== "" && value !== null;

  return (
    <div className={`p-4 rounded-xl border transition-colors ${
      isAnswered
        ? "bg-violet-500/5 border-violet-500/20"
        : "bg-white/[0.02] border-white/10"
    }`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <label className="text-sm font-medium text-white flex-1">
          {question.question_it}
          {question.required && (
            <span className="ml-1 text-red-400">*</span>
          )}
        </label>
        {isAnswered && (
          <CheckIcon className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        )}
      </div>

      {question.type === "text" && (
        <div className="space-y-2">
          <textarea
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={language === "en" ? "Type your answer..." : "Scrivi la tua risposta..."}
            rows={3}
            className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500/50 resize-none"
          />
          {!isAnswered && (
            <button
              onClick={() => onChange("__ai_generate__")}
              className="flex items-center gap-1.5 text-xs text-violet-400 hover:text-violet-300 transition-colors"
            >
              <SparklesIcon className="w-3.5 h-3.5" />
              {language === "en" ? "Let AI generate this" : "Lascia generare all'AI"}
            </button>
          )}
        </div>
      )}

      {question.type === "image_upload" && (
        <div className="space-y-2">
          {value && Array.isArray(value) && value.length > 0 ? (
            <div className="flex items-center gap-2 text-sm text-emerald-400">
              <PhotoIcon className="w-4 h-4" />
              <span>{value.length} {language === "en" ? "image(s) selected" : "immagine/i selezionata/e"}</span>
              <button
                onClick={() => onChange(null)}
                className="ml-auto text-slate-400 hover:text-red-400"
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <label className="flex flex-col items-center gap-2 p-4 border border-dashed border-white/10 rounded-lg cursor-pointer hover:border-violet-500/30 transition-colors">
              <PhotoIcon className="w-6 h-6 text-slate-500" />
              <span className="text-xs text-slate-400">
                {language === "en" ? "Click to upload images" : "Clicca per caricare immagini"}
              </span>
              <input
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  if (files.length === 0) return;
                  const readers = files.map(f => {
                    return new Promise<string>((resolve) => {
                      const reader = new FileReader();
                      reader.onload = () => resolve(reader.result as string);
                      reader.readAsDataURL(f);
                    });
                  });
                  Promise.all(readers).then(dataUrls => onChange(dataUrls));
                }}
              />
            </label>
          )}
          {!isAnswered && (
            <button
              onClick={() => onChange("__ai_generate__")}
              className="flex items-center gap-1.5 text-xs text-violet-400 hover:text-violet-300 transition-colors"
            >
              <SparklesIcon className="w-3.5 h-3.5" />
              {language === "en" ? "Generate images with AI" : "Genera immagini con AI"}
            </button>
          )}
        </div>
      )}

      {question.type === "choice" && question.options && (
        <div className="space-y-1.5">
          {question.options.map((opt) => (
            <button
              key={opt}
              onClick={() => onChange(opt)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                value === opt
                  ? "bg-violet-500/20 border border-violet-500/30 text-white"
                  : "bg-white/5 border border-white/5 text-slate-300 hover:bg-white/10"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {question.type === "toggle" && (
        <button
          onClick={() => onChange(!value)}
          className="flex items-center gap-3"
        >
          <div className={`w-10 h-5 rounded-full transition-colors relative ${
            value ? "bg-violet-500" : "bg-white/10"
          }`}>
            <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
              value ? "translate-x-[22px]" : "translate-x-0.5"
            }`} />
          </div>
          <span className="text-sm text-slate-300">
            {value
              ? (language === "en" ? "Yes" : "Si")
              : (language === "en" ? "No" : "No")}
          </span>
        </button>
      )}
    </div>
  );
}
