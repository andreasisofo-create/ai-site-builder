"use client";

import { useState, useEffect, useCallback } from "react";
import { API_BASE } from "@/lib/api";
import {
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock,
  Loader2,
  ExternalLink,
  Save,
  ChevronRight,
  ChevronLeft,
  TestTube,
  Send,
  Eye,
  EyeOff,
  Sparkles,
  Search,
  Share2,
  Bell,
  Bot,
  Brain,
} from "lucide-react";

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
function adminFetch(path: string, options: RequestInit = {}) {
  const token = sessionStorage.getItem("admin_token");
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  }).then((res) => {
    if (res.status === 401) {
      sessionStorage.removeItem("admin_token");
      throw new Error("SESSION_EXPIRED");
    }
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  });
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type PlatformStatus = "not_configured" | "pending_approval" | "test_mode" | "active";

interface StepConfig {
  id: string;
  platform: string;
  label: string;
  icon: typeof Search;
  description: string;
  docUrl: string;
  fields: FieldConfig[];
  instructions: string[];
}

interface FieldConfig {
  key: string;
  label: string;
  type: "text" | "password" | "url";
  placeholder: string;
  required?: boolean;
}

// ---------------------------------------------------------------------------
// Steps configuration
// ---------------------------------------------------------------------------
const STEPS: StepConfig[] = [
  {
    id: "google",
    platform: "google",
    label: "Google Ads API",
    icon: Search,
    description: "Collega il tuo account Google Ads per creare e gestire campagne Search e Display.",
    docUrl: "https://developers.google.com/google-ads/api/docs/get-started/introduction",
    fields: [
      { key: "developer_token", label: "Developer Token", type: "password", placeholder: "Il tuo Developer Token Google Ads", required: true },
      { key: "client_id", label: "OAuth Client ID", type: "password", placeholder: "Client ID dal progetto Google Cloud" },
      { key: "client_secret", label: "OAuth Client Secret", type: "password", placeholder: "Client Secret" },
      { key: "refresh_token", label: "Refresh Token", type: "password", placeholder: "Token di refresh OAuth" },
      { key: "mcc_id", label: "MCC ID (Manager Account)", type: "text", placeholder: "es. 123-456-7890" },
    ],
    instructions: [
      "Crea un account MCC (Manager Account) su ads.google.com/home/tools/manager-accounts",
      "Vai su Google Cloud Console e crea un progetto OAuth 2.0",
      "Richiedi il Developer Token dalla sezione API Center dell'MCC",
      "Il token inizia in modalita test (accesso solo ad account di test)",
      "Per accesso produzione, compila il modulo di richiesta Google",
    ],
  },
  {
    id: "meta",
    platform: "meta",
    label: "Meta Marketing API",
    icon: Share2,
    description: "Collega Meta Business Suite per campagne Facebook e Instagram.",
    docUrl: "https://developers.facebook.com/docs/marketing-apis/get-started",
    fields: [
      { key: "system_user_token", label: "System User Token", type: "password", placeholder: "Token dello System User", required: true },
      { key: "app_id", label: "App ID", type: "password", placeholder: "ID dell'app Meta" },
      { key: "app_secret", label: "App Secret", type: "password", placeholder: "Secret dell'app" },
      { key: "business_id", label: "Business ID", type: "text", placeholder: "ID del Business Manager" },
      { key: "pixel_id", label: "Pixel ID", type: "text", placeholder: "ID del Meta Pixel" },
    ],
    instructions: [
      "Accedi a business.facebook.com e crea un Business Manager",
      "In Impostazioni Business > System Users, crea uno System User",
      "Genera un token con permessi: ads_management, ads_read, pages_read",
      "Crea un'app su developers.facebook.com (tipo: Business)",
      "Installa il Meta Pixel sul sito del cliente per il tracking",
    ],
  },
  {
    id: "dataforseo",
    platform: "dataforseo",
    label: "API Ricerca (DataForSEO)",
    icon: Search,
    description: "Abilita la ricerca di mercato con keyword research, analisi competitor e volumi di ricerca.",
    docUrl: "https://dataforseo.com/apis",
    fields: [
      { key: "login", label: "Login / Email", type: "text", placeholder: "La tua email DataForSEO", required: true },
      { key: "password", label: "Password API", type: "password", placeholder: "Password API DataForSEO", required: true },
    ],
    instructions: [
      "Registrati su app.dataforseo.com/register",
      "DataForSEO offre $1 di credito gratuito per testare",
      "Usa le API SERP e Keywords Data per ricerche di mercato",
      "Alternativa: puoi usare Google Keyword Planner (richiede Google Ads attivo)",
      "I costi partono da $0.001 per richiesta keyword",
    ],
  },
  {
    id: "n8n",
    platform: "n8n",
    label: "n8n Automazione",
    icon: Bot,
    description: "Collega n8n per automatizzare i workflow: reporting, alert, sincronizzazione dati.",
    docUrl: "https://docs.n8n.io/api/",
    fields: [
      { key: "base_url", label: "n8n Base URL", type: "url", placeholder: "https://tuo-n8n.app.n8n.cloud", required: true },
      { key: "api_key", label: "API Key", type: "password", placeholder: "API key n8n" },
    ],
    instructions: [
      "Installa n8n self-hosted o usa n8n Cloud (n8n.io)",
      "In Settings > API, genera una API Key",
      "Configura i webhook per ricevere eventi dalla piattaforma",
      "Workflow consigliati: report giornaliero, alert budget, sync leads",
      "La connessione verra testata chiamando /api/v1/workflows",
    ],
  },
  {
    id: "telegram",
    platform: "telegram",
    label: "Notifiche (Telegram)",
    icon: Bell,
    description: "Ricevi notifiche in tempo reale su Telegram per alert, report e decisioni AI.",
    docUrl: "https://core.telegram.org/bots#botfather",
    fields: [
      { key: "bot_token", label: "Bot Token", type: "password", placeholder: "Token dal BotFather", required: true },
      { key: "chat_id", label: "Chat ID", type: "text", placeholder: "Il tuo Chat ID numerico", required: true },
    ],
    instructions: [
      "Apri Telegram e cerca @BotFather",
      "Invia /newbot e segui le istruzioni per creare il bot",
      "Copia il token API che BotFather ti fornisce",
      "Per ottenere il Chat ID: scrivi al bot, poi visita api.telegram.org/bot<TOKEN>/getUpdates",
      "Il Chat ID e un numero (es. 123456789) nel campo 'chat.id'",
    ],
  },
  {
    id: "ai",
    platform: "ai",
    label: "Modelli AI",
    icon: Brain,
    description: "Configura modelli AI aggiuntivi. Kimi K2.5 e sempre integrato nel sistema.",
    docUrl: "https://docs.anthropic.com/en/api/getting-started",
    fields: [
      { key: "claude_api_key", label: "Claude API Key (opzionale)", type: "password", placeholder: "sk-ant-..." },
      { key: "openai_api_key", label: "OpenAI API Key (opzionale)", type: "password", placeholder: "sk-..." },
    ],
    instructions: [
      "Kimi K2.5 e il modello principale, sempre attivo (nessuna configurazione necessaria)",
      "Claude (Anthropic): ideale per analisi strategiche e copywriting avanzato",
      "OpenAI GPT-4: utile per generazione creativa e varianti A/B",
      "Le API key sono opzionali - il sistema funziona con solo Kimi K2.5",
      "I costi dipendono dall'uso: ~$0.01-0.05 per richiesta AI",
    ],
  },
];

// ---------------------------------------------------------------------------
// Status badge component
// ---------------------------------------------------------------------------
function StatusBadge({ status }: { status: PlatformStatus }) {
  const config: Record<PlatformStatus, { label: string; bg: string; text: string; icon: typeof CheckCircle }> = {
    not_configured: { label: "Non configurato", bg: "bg-gray-500/10", text: "text-gray-400", icon: Clock },
    pending_approval: { label: "In attesa", bg: "bg-violet-500/10", text: "text-violet-400", icon: AlertTriangle },
    test_mode: { label: "Test Mode", bg: "bg-blue-500/10", text: "text-blue-400", icon: TestTube },
    active: { label: "Attivo", bg: "bg-emerald-500/10", text: "text-emerald-400", icon: CheckCircle },
  };

  const c = config[status] || config.not_configured;
  const Icon = c.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <Icon className="w-3 h-3" />
      {c.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export default function SetupWizardPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [statuses, setStatuses] = useState<Record<string, PlatformStatus>>({});
  const [configuredCount, setConfiguredCount] = useState(0);
  const [formData, setFormData] = useState<Record<string, Record<string, string>>>({});
  const [visibleFields, setVisibleFields] = useState<Record<string, boolean>>({});
  const [savedConfig, setSavedConfig] = useState<Record<string, Record<string, string | null>>>({});

  const currentStep = STEPS[activeStep];

  // Load config status
  const loadStatus = useCallback(async () => {
    try {
      const [statusRes, configRes] = await Promise.all([
        adminFetch("/api/ads/config/status"),
        adminFetch("/api/ads/config"),
      ]);
      if (statusRes.success) {
        setStatuses(statusRes.data.platforms);
        setConfiguredCount(statusRes.data.configured);
      }
      if (configRes.success) {
        setSavedConfig(configRes.data);
      }
    } catch (err) {
      console.error("Failed to load config:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  // Save platform config
  const handleSave = async () => {
    const stepFields = formData[currentStep.platform] || {};
    const nonEmpty = Object.fromEntries(
      Object.entries(stepFields).filter(([, v]) => v && v.trim())
    );
    if (Object.keys(nonEmpty).length === 0) return;

    setSaving(true);
    setTestResult(null);
    try {
      await adminFetch(`/api/ads/config/${currentStep.platform}`, {
        method: "PUT",
        body: JSON.stringify({ fields: nonEmpty }),
      });
      // Clear form data for saved fields and reload
      setFormData((prev) => ({ ...prev, [currentStep.platform]: {} }));
      await loadStatus();
    } catch (err) {
      console.error("Save error:", err);
    } finally {
      setSaving(false);
    }
  };

  // Test connection
  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await adminFetch(`/api/ads/config/${currentStep.platform}/test`, {
        method: "POST",
      });
      if (res.success && res.data) {
        setTestResult({ success: res.data.success, message: res.data.message });
        await loadStatus();
      }
    } catch (err) {
      setTestResult({ success: false, message: "Errore di connessione al server" });
    } finally {
      setTesting(false);
    }
  };

  // Update field value
  const updateField = (platform: string, key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [platform]: { ...(prev[platform] || {}), [key]: value },
    }));
  };

  // Toggle field visibility (for password fields)
  const toggleVisibility = (fieldKey: string) => {
    setVisibleFields((prev) => ({ ...prev, [fieldKey]: !prev[fieldKey] }));
  };

  // Get masked saved value for display
  const getSavedValue = (platform: string, fieldKey: string): string | null => {
    const platformData = savedConfig[platform];
    if (!platformData) return null;
    const val = platformData[fieldKey];
    return typeof val === "string" ? val : null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-500/20 via-[#141420] to-[#0a0a0f] border border-violet-500/20 p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-5 h-5 text-violet-400" />
            <span className="text-violet-400 text-sm font-medium uppercase tracking-wider">
              Setup Integrazioni
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Configurazione Piattaforme</h1>
          <p className="text-gray-400 max-w-xl mb-4">
            Configura le integrazioni esterne per attivare la pipeline AI ADS completa.
          </p>

          {/* Progress bar */}
          <div className="flex items-center gap-4">
            <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${(configuredCount / STEPS.length) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-violet-400">
              {configuredCount}/{STEPS.length} configurati
            </span>
          </div>
        </div>
      </div>

      {/* Main layout: sidebar + content */}
      <div className="flex gap-6">
        {/* Left sidebar: step list */}
        <div className="w-72 shrink-0">
          <div className="rounded-xl bg-[#141420] border border-white/5 p-4 space-y-1 sticky top-8">
            {STEPS.map((step, idx) => {
              const Icon = step.icon;
              const status = statuses[step.platform] || "not_configured";
              const isActive = idx === activeStep;
              const isConfigured = status !== "not_configured";

              return (
                <button
                  key={step.id}
                  onClick={() => {
                    setActiveStep(idx);
                    setTestResult(null);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all text-left text-sm ${
                    isActive
                      ? "bg-violet-500/10 text-violet-400 border border-violet-500/20"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    isConfigured
                      ? "bg-emerald-500/10"
                      : isActive
                      ? "bg-violet-500/10"
                      : "bg-white/5"
                  }`}>
                    {isConfigured ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Icon className={`w-4 h-4 ${isActive ? "text-violet-400" : "text-gray-500"}`} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{step.label}</p>
                    <p className="text-xs text-gray-500">
                      {status === "active" ? "Attivo" : status === "test_mode" ? "Test" : status === "pending_approval" ? "In attesa" : "Da configurare"}
                    </p>
                  </div>
                  <span className={`w-2 h-2 rounded-full shrink-0 ${
                    isConfigured ? "bg-emerald-400" : "bg-gray-600"
                  }`} />
                </button>
              );
            })}
          </div>
        </div>

        {/* Right content area */}
        <div className="flex-1 min-w-0">
          <div className="rounded-xl bg-[#141420] border border-white/5 p-6 space-y-6">
            {/* Step header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-violet-500/10 flex items-center justify-center">
                  {(() => { const Icon = currentStep.icon; return <Icon className="w-6 h-6 text-violet-400" />; })()}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{currentStep.label}</h2>
                  <p className="text-sm text-gray-400 mt-1">{currentStep.description}</p>
                </div>
              </div>
              <StatusBadge status={statuses[currentStep.platform] || "not_configured"} />
            </div>

            {/* Kimi K2.5 badge for AI step */}
            {currentStep.platform === "ai" && (
              <div className="flex items-center gap-3 p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <div>
                  <p className="text-sm font-medium text-emerald-400">Kimi K2.5 - Integrato</p>
                  <p className="text-xs text-gray-400">Modello principale sempre attivo. Le API key sotto sono opzionali.</p>
                </div>
                <StatusBadge status="active" />
              </div>
            )}

            {/* Instructions */}
            <div className="p-4 rounded-lg bg-[#0a0a0f] border border-white/5">
              <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-violet-400" />
                Come configurare
              </h3>
              <ol className="space-y-2">
                {currentStep.instructions.map((instruction, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-gray-400">
                    <span className="w-5 h-5 rounded-full bg-violet-500/10 text-violet-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{instruction}</span>
                  </li>
                ))}
              </ol>
              <a
                href={currentStep.docUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 mt-4 text-sm text-violet-400 hover:text-violet-300 transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Documentazione ufficiale
              </a>
            </div>

            {/* Form fields */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-white">Credenziali</h3>
              {currentStep.fields.map((field) => {
                const fieldId = `${currentStep.platform}_${field.key}`;
                const currentValue = formData[currentStep.platform]?.[field.key] || "";
                const savedValue = getSavedValue(currentStep.platform, field.key);
                const isVisible = visibleFields[fieldId];
                const isPasswordField = field.type === "password";

                return (
                  <div key={field.key}>
                    <label className="block text-sm text-gray-400 mb-1.5">
                      {field.label}
                      {field.required && <span className="text-violet-400 ml-1">*</span>}
                    </label>
                    <div className="relative">
                      <input
                        type={isPasswordField && !isVisible ? "password" : "text"}
                        value={currentValue}
                        onChange={(e) => updateField(currentStep.platform, field.key, e.target.value)}
                        placeholder={savedValue ? `Salvato: ${savedValue}` : field.placeholder}
                        className="w-full px-4 py-2.5 rounded-lg bg-[#0a0a0f] border border-white/10 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20 transition-colors pr-10"
                      />
                      {isPasswordField && (
                        <button
                          type="button"
                          onClick={() => toggleVisibility(fieldId)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                        >
                          {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      )}
                    </div>
                    {savedValue && (
                      <p className="text-xs text-gray-600 mt-1">Valore attuale: {savedValue}</p>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Test result */}
            {testResult && (
              <div className={`p-4 rounded-lg border ${
                testResult.success
                  ? "bg-emerald-500/5 border-emerald-500/20"
                  : "bg-red-500/5 border-red-500/20"
              }`}>
                <div className="flex items-center gap-2">
                  {testResult.success ? (
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                  )}
                  <p className={`text-sm font-medium ${
                    testResult.success ? "text-emerald-400" : "text-red-400"
                  }`}>
                    {testResult.message}
                  </p>
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-white/5">
              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-500 text-white font-medium text-sm hover:bg-violet-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  Salva
                </button>
                <button
                  onClick={handleTest}
                  disabled={testing}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-white/10 text-white font-medium text-sm hover:bg-white/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {testing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : currentStep.platform === "telegram" ? (
                    <Send className="w-4 h-4" />
                  ) : (
                    <TestTube className="w-4 h-4" />
                  )}
                  {currentStep.platform === "telegram" ? "Invia Messaggio di Test" : "Testa Connessione"}
                </button>
              </div>

              <div className="flex gap-2">
                {activeStep > 0 && (
                  <button
                    onClick={() => {
                      setActiveStep(activeStep - 1);
                      setTestResult(null);
                    }}
                    className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors text-sm"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Precedente
                  </button>
                )}
                {activeStep < STEPS.length - 1 && (
                  <button
                    onClick={() => {
                      setActiveStep(activeStep + 1);
                      setTestResult(null);
                    }}
                    className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-white/5 text-white hover:bg-white/10 transition-colors text-sm"
                  >
                    Successivo
                    <ChevronRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
