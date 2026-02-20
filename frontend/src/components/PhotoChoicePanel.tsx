"use client";

import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ImageIcon,
  Upload,
  Sparkles,
  Check,
  X,
  CheckCircle2,
  Clock,
  Images,
} from "lucide-react";

// ============ TYPES ============

export interface PhotoChoice {
  section_type: string;
  section_label: string;
  placeholder_key: string;
  stock_preview_url: string;
  current_url: string;
}

export interface PhotoDecision {
  section_type: string;
  placeholder_key: string;
  action: "stock" | "upload" | "retry";
  photo_url?: string;
}

export interface PhotoChoicePanelProps {
  choices: PhotoChoice[];
  onConfirm: (decisions: PhotoDecision[]) => void;
  onCancel: () => void;
  onUploadFile?: (file: File) => Promise<string>;
}

// ============ SECTION LABEL MAP ============

const SECTION_LABELS: Record<string, string> = {
  hero: "Sezione Hero",
  about: "Chi Siamo",
  services: "Servizi",
  gallery: "Galleria",
  portfolio: "Portfolio",
  team: "Il Team",
  testimonials: "Testimonianze",
  contact: "Contatti",
  features: "Funzionalita'",
  pricing: "Prezzi",
  cta: "Call to Action",
  blog: "Blog",
  faq: "FAQ",
  stats: "Statistiche",
  menu: "Menu",
};

function getSectionLabel(choice: PhotoChoice): string {
  if (choice.section_label) return choice.section_label;
  return SECTION_LABELS[choice.section_type] || choice.section_type;
}

// ============ MAX FILE SIZE ============

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

// ============ SINGLE PHOTO CARD ============

interface CardDecision {
  action: "stock" | "upload" | "retry";
  previewUrl?: string;
}

function PhotoCard({
  choice,
  decision,
  onChooseStock,
  onChooseUpload,
  onChooseRetry,
  onUploadFile,
}: {
  choice: PhotoChoice;
  decision: CardDecision | null;
  onChooseStock: () => void;
  onChooseUpload: (url: string) => void;
  onChooseRetry: () => void;
  onUploadFile?: (file: File) => Promise<string>;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [stockLoaded, setStockLoaded] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const isChosen = decision !== null;

  const handleFile = useCallback(
    async (file: File) => {
      setUploadError(null);

      if (!ACCEPTED_TYPES.includes(file.type)) {
        setUploadError("Formato non supportato. Usa JPG, PNG o WebP.");
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        setUploadError("File troppo grande. Massimo 5MB.");
        return;
      }

      // Show local preview immediately
      const localUrl = URL.createObjectURL(file);
      setUploadPreview(localUrl);
      setUploading(true);

      try {
        if (onUploadFile) {
          const remoteUrl = await onUploadFile(file);
          onChooseUpload(remoteUrl);
        } else {
          // Fallback: use local blob URL
          onChooseUpload(localUrl);
        }
      } catch {
        setUploadError("Errore durante il caricamento. Riprova.");
        setUploadPreview(null);
      } finally {
        setUploading(false);
      }
    },
    [onChooseUpload, onUploadFile]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
      // Reset input so same file can be selected again
      e.target.value = "";
    },
    [handleFile]
  );

  // Determine which preview to show
  const displayUrl =
    decision?.action === "upload" && (uploadPreview || decision.previewUrl)
      ? uploadPreview || decision.previewUrl
      : choice.stock_preview_url;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative rounded-xl border transition-colors duration-300 overflow-hidden ${
        isChosen
          ? "border-emerald-500/30 bg-emerald-500/[0.03]"
          : "border-white/10 bg-[#16162a]"
      }`}
    >
      {/* Status badge */}
      <div className="absolute top-3 right-3 z-10">
        {isChosen ? (
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-medium">
            <CheckCircle2 className="w-3 h-3" />
            <span>Scelta</span>
          </div>
        ) : (
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 text-slate-500 text-[10px]">
            <Clock className="w-3 h-3" />
            <span>In attesa</span>
          </div>
        )}
      </div>

      {/* Section label */}
      <div className="px-4 pt-4 pb-2">
        <h3 className="text-sm font-semibold text-white">
          {getSectionLabel(choice)}
        </h3>
        <p className="text-[10px] text-slate-500 mt-0.5">
          {choice.placeholder_key}
        </p>
      </div>

      {/* Image preview area */}
      <div
        className={`mx-4 mb-3 relative rounded-lg overflow-hidden border transition-colors ${
          isDragging
            ? "border-blue-500/50 bg-blue-500/10"
            : "border-white/5 bg-black/20"
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="relative w-full h-[140px] sm:h-[160px]">
          {/* Blur-up placeholder */}
          {!stockLoaded && !uploadPreview && (
            <div className="absolute inset-0 bg-white/[0.03] animate-pulse" />
          )}

          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={displayUrl}
            alt={getSectionLabel(choice)}
            className={`w-full h-full object-cover transition-all duration-500 ${
              stockLoaded || uploadPreview ? "opacity-100 blur-0" : "opacity-0 blur-sm"
            }`}
            onLoad={() => setStockLoaded(true)}
          />

          {/* Upload overlay when dragging */}
          {isDragging && (
            <div className="absolute inset-0 flex items-center justify-center bg-blue-500/20 backdrop-blur-sm">
              <div className="text-center">
                <Upload className="w-8 h-8 text-blue-400 mx-auto mb-1" />
                <p className="text-xs text-blue-300">Rilascia qui</p>
              </div>
            </div>
          )}

          {/* Uploading spinner */}
          {uploading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
              <div className="w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            </div>
          )}

          {/* Action label overlay */}
          {isChosen && !uploading && (
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent px-3 py-2">
              <span className="text-[10px] text-white/80">
                {decision.action === "stock" && "Foto stock selezionata"}
                {decision.action === "upload" && "Foto caricata"}
                {decision.action === "retry" && "Rigenerazione AI richiesta"}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Error message */}
      {uploadError && (
        <div className="mx-4 mb-2 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-[10px] text-red-400">{uploadError}</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="px-4 pb-4 flex gap-2">
        <button
          onClick={onChooseStock}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
            decision?.action === "stock"
              ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/30"
              : "bg-white/5 text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-400"
          }`}
        >
          <ImageIcon className="w-3.5 h-3.5" />
          <span>Usa stock</span>
        </button>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
            decision?.action === "upload"
              ? "bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/30"
              : "bg-white/5 text-slate-400 hover:bg-blue-500/10 hover:text-blue-400"
          } ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Carica</span>
        </button>

        <button
          onClick={onChooseRetry}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
            decision?.action === "retry"
              ? "bg-violet-500/20 text-violet-400 ring-1 ring-violet-500/30"
              : "bg-white/5 text-slate-400 hover:bg-violet-500/10 hover:text-violet-400"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Rigenera AI</span>
        </button>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp"
        className="hidden"
        onChange={handleFileInput}
      />
    </motion.div>
  );
}

// ============ MAIN PANEL ============

export default function PhotoChoicePanel({
  choices,
  onConfirm,
  onCancel,
  onUploadFile,
}: PhotoChoicePanelProps) {
  const [decisions, setDecisions] = useState<Record<string, CardDecision>>({});

  const completedCount = Object.keys(decisions).length;
  const totalCount = choices.length;
  const allChosen = completedCount === totalCount;

  const setDecision = useCallback(
    (key: string, action: CardDecision["action"], previewUrl?: string) => {
      setDecisions((prev) => ({
        ...prev,
        [key]: { action, previewUrl },
      }));
    },
    []
  );

  const handleUseStockAll = useCallback(() => {
    const bulk: Record<string, CardDecision> = {};
    for (const c of choices) {
      bulk[c.placeholder_key] = { action: "stock" };
    }
    setDecisions(bulk);
  }, [choices]);

  const handleConfirm = useCallback(() => {
    const result: PhotoDecision[] = choices.map((c) => {
      const d = decisions[c.placeholder_key];
      return {
        section_type: c.section_type,
        placeholder_key: c.placeholder_key,
        action: d?.action || "stock",
        photo_url: d?.action === "upload" ? d.previewUrl : undefined,
      };
    });
    onConfirm(result);
  }, [choices, decisions, onConfirm]);

  return (
    <AnimatePresence>
      <motion.div
        key="photo-choice-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={onCancel}
        />

        {/* Panel */}
        <motion.div
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "100%", opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="relative z-10 w-full max-w-3xl max-h-[90vh] bg-[#0e0e1a] border border-white/10 rounded-t-2xl sm:rounded-2xl shadow-2xl shadow-black/50 flex flex-col"
        >
          {/* Header */}
          <div className="shrink-0 px-5 pt-5 pb-3 border-b border-white/5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center">
                  <Images className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">
                    Scegli le foto per il tuo sito
                  </h2>
                  <p className="text-xs text-slate-500">
                    {completedCount} di {totalCount} completate
                  </p>
                </div>
              </div>
              <button
                onClick={onCancel}
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Progress bar */}
            <div className="w-full h-1 rounded-full bg-white/5 overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
                initial={{ width: 0 }}
                animate={{
                  width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%`,
                }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />
            </div>

            {/* Quick action */}
            <button
              onClick={handleUseStockAll}
              className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-xs text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-400 transition-colors"
            >
              <Check className="w-3.5 h-3.5" />
              Usa stock per tutte
            </button>
          </div>

          {/* Scrollable card grid */}
          <div className="flex-1 overflow-y-auto px-5 py-4 min-h-0">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {choices.map((choice) => (
                <PhotoCard
                  key={choice.placeholder_key}
                  choice={choice}
                  decision={decisions[choice.placeholder_key] || null}
                  onChooseStock={() =>
                    setDecision(choice.placeholder_key, "stock")
                  }
                  onChooseUpload={(url) =>
                    setDecision(choice.placeholder_key, "upload", url)
                  }
                  onChooseRetry={() =>
                    setDecision(choice.placeholder_key, "retry")
                  }
                  onUploadFile={onUploadFile}
                />
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="shrink-0 px-5 py-4 border-t border-white/5 flex items-center justify-between gap-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-lg text-xs text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
            >
              Annulla
            </button>
            <button
              onClick={handleConfirm}
              disabled={!allChosen}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium transition-all ${
                allChosen
                  ? "bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-lg shadow-violet-500/20 hover:shadow-violet-500/40 hover:scale-[1.02] active:scale-[0.98]"
                  : "bg-white/5 text-slate-600 cursor-not-allowed"
              }`}
            >
              <Check className="w-4 h-4" />
              Conferma e continua generazione
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
