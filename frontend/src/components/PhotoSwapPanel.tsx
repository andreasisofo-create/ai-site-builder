"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PhotoIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowUpTrayIcon,
  CheckIcon,
  CameraIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import {
  getPhotoMap,
  swapPhoto,
  uploadMedia,
  PhotoMapItem,
} from "@/lib/api";

// ============ TYPES ============

interface PhotoCardState {
  status: "pending" | "kept" | "uploaded";
  newUrl?: string;
  previewUrl?: string;
}

interface PhotoSwapPanelProps {
  siteId: number;
  onClose: () => void;
  onPhotoSwapped: () => void;
  language: string;
}

// ============ PHOTO CARD ============

function SwapCard({
  photo,
  cardState,
  siteId,
  language,
  onStateChange,
}: {
  photo: PhotoMapItem;
  cardState: PhotoCardState;
  siteId: number;
  language: string;
  onStateChange: (state: PhotoCardState) => void;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  const displayUrl = cardState.previewUrl || photo.current_url;

  const handleKeepStock = async () => {
    try {
      await swapPhoto(siteId, photo.id, "keep_stock");
      onStateChange({ status: "kept" });
    } catch {
      toast.error(
        language === "en" ? "Error keeping photo" : "Errore nel mantenere la foto"
      );
    }
  };

  const handleUpload = async (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      toast.error(
        language === "en" ? "File too large (max 5MB)" : "File troppo grande (max 5MB)"
      );
      return;
    }
    setUploading(true);
    const localPreview = URL.createObjectURL(file);
    onStateChange({ status: "pending", previewUrl: localPreview });

    try {
      const uploaded = await uploadMedia(siteId, file);
      const result = await swapPhoto(siteId, photo.id, "upload", uploaded.url);
      onStateChange({
        status: "uploaded",
        newUrl: result.new_url,
        previewUrl: localPreview,
      });
      toast.success(
        language === "en" ? "Photo replaced!" : "Foto sostituita!"
      );
    } catch {
      onStateChange({ status: "pending" });
      toast.error(
        language === "en" ? "Upload error" : "Errore nel caricamento"
      );
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    e.target.value = "";
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative rounded-xl border transition-colors overflow-hidden ${
        cardState.status === "kept"
          ? "border-emerald-500/30 bg-emerald-500/[0.03]"
          : cardState.status === "uploaded"
          ? "border-blue-500/30 bg-blue-500/[0.03]"
          : "border-white/10 bg-[#16162a]"
      }`}
    >
      {/* Status badge */}
      <div className="absolute top-2 right-2 z-10">
        {cardState.status === "kept" && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-medium">
            <CheckCircleIcon className="w-3 h-3" />
            Stock
          </span>
        )}
        {cardState.status === "uploaded" && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[10px] font-medium">
            <CheckCircleIcon className="w-3 h-3" />
            {language === "en" ? "Custom" : "Personalizzata"}
          </span>
        )}
        {photo.is_stock && cardState.status === "pending" && (
          <span className="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 text-[10px]">
            Stock
          </span>
        )}
      </div>

      {/* Thumbnail */}
      <div className="relative w-full h-[130px]">
        {!imgLoaded && (
          <div className="absolute inset-0 bg-white/[0.03] animate-pulse" />
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={displayUrl}
          alt={photo.label}
          className={`w-full h-full object-cover transition-all duration-300 ${
            imgLoaded ? "opacity-100" : "opacity-0"
          }`}
          onLoad={() => setImgLoaded(true)}
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='130' fill='%23222'%3E%3Crect width='200' height='130'/%3E%3Ctext x='50%25' y='50%25' fill='%23555' text-anchor='middle' dy='.3em' font-size='12'%3EFoto%3C/text%3E%3C/svg%3E";
            setImgLoaded(true);
          }}
        />
        {uploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <ArrowPathIcon className="w-6 h-6 text-blue-400 animate-spin" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="px-3 pt-2.5 pb-1.5">
        <h4 className="text-xs font-semibold text-white leading-tight">
          {photo.label}
        </h4>
        <p className="text-[10px] text-slate-500 mt-0.5 leading-relaxed">
          {photo.description}
        </p>
        <p className="text-[10px] text-slate-600 mt-0.5">{photo.size_hint}</p>
      </div>

      {/* Actions */}
      <div className="px-3 pb-3 flex gap-1.5">
        <button
          onClick={handleKeepStock}
          disabled={uploading}
          className={`flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
            cardState.status === "kept"
              ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/30"
              : "bg-white/5 text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-400"
          }`}
        >
          <CheckIcon className="w-3 h-3" />
          {language === "en" ? "Keep this" : "Tieni questa"}
        </button>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className={`flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
            cardState.status === "uploaded"
              ? "bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/30"
              : "bg-white/5 text-slate-400 hover:bg-blue-500/10 hover:text-blue-400"
          } ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <ArrowUpTrayIcon className="w-3 h-3" />
          {language === "en" ? "Upload yours" : "Carica la tua"}
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />
    </motion.div>
  );
}

// ============ MAIN PANEL ============

export default function PhotoSwapPanel({
  siteId,
  onClose,
  onPhotoSwapped,
  language,
}: PhotoSwapPanelProps) {
  const [photos, setPhotos] = useState<PhotoMapItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cardStates, setCardStates] = useState<Record<string, PhotoCardState>>({});

  useEffect(() => {
    loadPhotoMap();
  }, [siteId]);

  const loadPhotoMap = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPhotoMap(siteId);
      setPhotos(data.photos);
      const initial: Record<string, PhotoCardState> = {};
      for (const p of data.photos) {
        initial[p.id] = { status: "pending" };
      }
      setCardStates(initial);
    } catch {
      setError(
        language === "en"
          ? "Could not load photo map"
          : "Impossibile caricare la mappa foto"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCardStateChange = useCallback(
    (photoId: string, state: PhotoCardState) => {
      setCardStates((prev) => ({ ...prev, [photoId]: state }));
      if (state.status === "uploaded") {
        onPhotoSwapped();
      }
    },
    [onPhotoSwapped]
  );

  const handleKeepAllStock = async () => {
    const pending = photos.filter(
      (p) => cardStates[p.id]?.status === "pending"
    );
    for (const p of pending) {
      try {
        await swapPhoto(siteId, p.id, "keep_stock");
        setCardStates((prev) => ({
          ...prev,
          [p.id]: { status: "kept" },
        }));
      } catch {
        // Continue with others
      }
    }
  };

  const completedCount = Object.values(cardStates).filter(
    (s) => s.status !== "pending"
  ).length;
  const customCount = Object.values(cardStates).filter(
    (s) => s.status === "uploaded"
  ).length;
  const totalCount = photos.length;
  const allDone = completedCount === totalCount && totalCount > 0;

  return (
    <>
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CameraIcon className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold">
            {language === "en" ? "Customize Photos" : "Personalizza foto"}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-white/5 rounded-lg transition-colors"
        >
          <XMarkIcon className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <ArrowPathIcon className="w-6 h-6 animate-spin text-slate-400" />
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-sm text-red-400 mb-3">{error}</p>
            <button
              onClick={loadPhotoMap}
              className="px-4 py-2 bg-white/5 rounded-lg text-xs text-slate-300 hover:bg-white/10 transition-colors"
            >
              {language === "en" ? "Retry" : "Riprova"}
            </button>
          </div>
        ) : photos.length === 0 ? (
          <div className="text-center py-8">
            <PhotoIcon className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="text-sm text-slate-400">
              {language === "en"
                ? "No photos found in the site"
                : "Nessuna foto trovata nel sito"}
            </p>
          </div>
        ) : (
          <>
            {/* Progress */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">
                  {customCount} {language === "en" ? "of" : "di"} {totalCount}{" "}
                  {language === "en" ? "photos customized" : "foto personalizzate"}
                </span>
                <span className="text-slate-500">
                  {completedCount}/{totalCount}
                </span>
              </div>
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
            </div>

            {/* Quick action */}
            <button
              onClick={handleKeepAllStock}
              className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-white/5 text-xs text-slate-400 hover:bg-emerald-500/10 hover:text-emerald-400 transition-colors border border-white/5 hover:border-emerald-500/20"
            >
              <CheckIcon className="w-3.5 h-3.5" />
              {language === "en" ? "Keep all stock photos" : "Usa stock per tutte"}
            </button>

            {/* Photo grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <AnimatePresence>
                {photos.map((photo) => (
                  <SwapCard
                    key={photo.id}
                    photo={photo}
                    cardState={cardStates[photo.id] || { status: "pending" }}
                    siteId={siteId}
                    language={language}
                    onStateChange={(state) =>
                      handleCardStateChange(photo.id, state)
                    }
                  />
                ))}
              </AnimatePresence>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      {!loading && photos.length > 0 && (
        <div className="shrink-0 p-4 border-t border-white/10">
          <button
            onClick={onClose}
            className={`w-full py-2.5 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2 ${
              allDone
                ? "bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:scale-[1.01] active:scale-[0.99]"
                : "bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            <CheckCircleIcon className="w-4 h-4" />
            {language === "en" ? "Confirm and close" : "Conferma e chiudi"}
          </button>
        </div>
      )}
    </>
  );
}
