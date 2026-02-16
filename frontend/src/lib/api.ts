/** Client API per comunicare con il backend */

// Chiama il backend Render direttamente (con CORS).
// Il proxy Vercel rewrite perde l'header Authorization su redirect cross-origin.
export const API_BASE = "https://ai-site-builder-jz2g.onrender.com";

/** Ottiene il token JWT dal localStorage */
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

/** Ottiene gli headers di autenticazione */
function getAuthHeaders(): Record<string, string> {
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

/** Gestisce le risposte API */
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Errore sconosciuto" }));

    // Se 401 Unauthorized, pulisci auth e redirect al login
    if (res.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/auth";
      }
      const authError = new Error(error.detail || "Non autorizzato");
      (authError as any).status = 401;
      throw authError;
    }

    // Se è un errore di quota, lancia con struttura specifica
    if (res.status === 403 && error.detail?.upgrade_required) {
      const quotaError = new Error(error.detail.message || "Quota esaurita");
      (quotaError as any).quota = error.detail;
      (quotaError as any).isQuotaError = true;
      throw quotaError;
    }
    throw new Error(error.detail?.message || error.detail || `Errore ${res.status}`);
  }
  return res.json();
}

// ============ USER / QUOTA ============

export interface UserQuota {
  is_premium: boolean;
  generations_used: number;
  generations_limit: number;
  remaining_generations: number;
  has_remaining_generations: boolean;
}

export async function getQuota(): Promise<UserQuota> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/auth/quota`, { headers });
  return handleResponse<UserQuota>(res);
}

export async function upgradeToPremium(): Promise<{ success: boolean; message: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/generate/upgrade`, {
    method: "POST",
    headers,
  });
  return handleResponse(res);
}

// ============ SITES ============

export interface Site {
  id: number;
  name: string;
  slug: string;
  description?: string;
  status: "draft" | "generating" | "ready" | "published";
  is_published: boolean;
  thumbnail?: string;
  html_content?: string;
  domain?: string;
  vercel_project_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateSiteData {
  name: string;
  slug: string;
  description?: string;
  template?: string;
}

export async function fetchSites(): Promise<Site[]> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/`, { headers });
  return handleResponse<Site[]>(res);
}

export async function createSite(data: CreateSiteData): Promise<Site> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
  return handleResponse<Site>(res);
}

export async function getSite(id: number): Promise<Site> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${id}`, { headers });
  return handleResponse<Site>(res);
}

export async function updateSite(
  id: number,
  data: Partial<Omit<Site, "id" | "created_at" | "updated_at">>
): Promise<Site> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${id}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(data),
  });
  return handleResponse<Site>(res);
}

export async function deleteSite(id: number): Promise<void> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${id}`, {
    method: "DELETE",
    headers,
  });
  await handleResponse(res);
}

export async function getSitePreview(id: number): Promise<{ html: string; name: string; status: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${id}/preview`, { headers });
  return handleResponse(res);
}

// ============ AI GENERATION ============

export interface GenerateRequest {
  business_name: string;
  business_description: string;
  sections?: string[];
  style_preferences?: {
    primary_color?: string;
    secondary_color?: string;
    font_family?: string;
    mood?: string;
  };
  reference_analysis?: string;
  reference_image_url?: string;
  photo_urls?: string[];
  logo_url?: string;
  contact_info?: Record<string, string>;
  site_id?: number;
  template_style_id?: string;
  generate_images?: boolean;
}

export interface GenerateResponse {
  success: boolean;
  html_content?: string;
  model_used?: string;
  tokens_input?: number;
  tokens_output?: number;
  cost_usd?: number;
  generation_time_ms?: number;
  pipeline_steps?: number;
  error?: string;
  quota?: {
    generations_used: number;
    generations_limit: number;
    remaining_generations: number;
    is_premium: boolean;
  };
}

export async function generateWebsite(data: GenerateRequest): Promise<GenerateResponse> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/generate/website`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
  return handleResponse<GenerateResponse>(res);
}

// ============ REFINE (CHAT AI) ============

export interface RefineRequest {
  site_id: number;
  message: string;
  section?: string;
  language?: string;
}

export interface RefineResponse {
  success: boolean;
  html_content?: string;
  error?: string;
  model_used?: string;
  generation_time_ms?: number;
  strategy?: "css_vars" | "text" | "section" | "structural";
}

export async function refineWebsite(data: RefineRequest): Promise<RefineResponse> {
  const headers = getAuthHeaders();
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180_000); // 3 min timeout
  try {
    const res = await fetch(`${API_BASE}/api/generate/refine`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
      signal: controller.signal,
    });
    return handleResponse<RefineResponse>(res);
  } catch (err: any) {
    if (err.name === "AbortError") {
      return { success: false, error: "Timeout: la modifica ha impiegato troppo tempo. Riprova con una richiesta piu' semplice." };
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ============ GENERATION STATUS ============

export interface GenerationStatus {
  site_id: number;
  status: string;
  is_generating: boolean;
  step: number;
  total_steps: number;
  percentage: number;
  message: string;
  preview_data?: {
    phase: "analyzing" | "theme_complete" | "content_complete" | "complete";
    colors?: { primary: string; secondary: string; accent: string; bg: string; text: string };
    font_heading?: string;
    font_body?: string;
    sections?: string[];
    hero_title?: string;
    hero_subtitle?: string;
    hero_cta?: string;
    services_titles?: string[];
  } | null;
}

export async function getGenerationStatus(siteId: number): Promise<GenerationStatus> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/generate/status/${siteId}`, { headers });
  return handleResponse<GenerationStatus>(res);
}

// ============ IMAGE GENERATION ============

export interface RegenerateImagesRequest {
  site_id: number;
  section_type: string;
  resolution?: string;
}

export interface ImagesResponse {
  images: string[];
  section_type: string;
  count: number;
}

export async function regenerateImages(data: RegenerateImagesRequest): Promise<ImagesResponse> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/images/regenerate`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
  return handleResponse<ImagesResponse>(res);
}

// ============ EXPORT ============

export async function exportSite(siteId: number, siteName: string): Promise<void> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${siteId}/export`, { headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Errore export" }));
    throw new Error(error.detail || "Errore durante l'export");
  }

  // Scarica come file
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${siteName.toLowerCase().replace(/\s+/g, "-")}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// ============ DEPLOY ============

export interface DeployResponse {
  success: boolean;
  site_id: number;
  deployment_id: string;
  url: string;
  project_id: string;
  status: string;
}

export interface DeployStatusResponse {
  site_id: number;
  is_published: boolean;
  status: string;
  domain: string | null;
  vercel_project_id: string | null;
  published_at: string | null;
  vercel_status?: string;
  vercel_url?: string;
}

export async function deploySite(siteId: number): Promise<DeployResponse> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/deploy/${siteId}`, {
    method: "POST",
    headers,
  });
  return handleResponse<DeployResponse>(res);
}

export async function getDeployStatus(siteId: number): Promise<DeployStatusResponse> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/deploy/${siteId}/status`, { headers });
  return handleResponse<DeployStatusResponse>(res);
}

// ============ COMPONENTS ============

export interface Component {
  id: number;
  name: string;
  type: string;
  content: object;
  styles: object;
  order: number;
  is_visible: boolean;
}

export async function fetchComponents(siteId: number): Promise<Component[]> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/components/site/${siteId}`, { headers });
  return handleResponse<Component[]>(res);
}

export async function createComponent(
  siteId: number,
  name: string,
  type: string,
  content?: object,
  styles?: object
): Promise<Component> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/components/`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      site_id: siteId,
      name,
      type,
      content: content || {},
      styles: styles || {},
    }),
  });
  return handleResponse<Component>(res);
}

// ============ PAYMENTS / REVOLUT ============

export interface CheckoutResponse {
  checkout_url: string;
  order_id: string;
}

export interface PaymentStatus {
  plan: string;
  plan_label: string;
  has_paid: boolean;
  revolut_customer_id: string | null;
}

export async function createCheckoutSession(plan: "base" | "premium"): Promise<CheckoutResponse> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/payments/create-checkout`, {
    method: "POST",
    headers,
    body: JSON.stringify({ plan }),
  });
  return handleResponse<CheckoutResponse>(res);
}

export async function getPaymentStatus(): Promise<PaymentStatus> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/payments/status`, { headers });
  return handleResponse<PaymentStatus>(res);
}

// ============ VERSIONS ============

export interface SiteVersionInfo {
  id: number;
  version_number: number;
  change_description: string;
  created_at: string;
}

export async function getSiteVersions(siteId: number): Promise<SiteVersionInfo[]> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${siteId}/versions`, { headers });
  return handleResponse<SiteVersionInfo[]>(res);
}

export async function rollbackSiteVersion(siteId: number, versionId: number): Promise<{ html_content: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/sites/${siteId}/versions/${versionId}/rollback`, {
    method: "POST",
    headers,
  });
  return handleResponse<{ html_content: string }>(res);
}

// ============ UNPUBLISH ============

export async function unpublishSite(siteId: number): Promise<{ success: boolean; message: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/deploy/${siteId}`, {
    method: "DELETE",
    headers,
  });
  return handleResponse(res);
}

// ============ CHAT (Help Chatbot) ============

export async function chatMessage(
  message: string,
  history: Array<{ role: string; content: string }>,
  language?: string
): Promise<{ reply: string; error?: string }> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history, language: language || "it" }),
  });
  if (!res.ok) {
    return { reply: "", error: `Errore ${res.status}` };
  }
  return res.json();
}

// ============ MEDIA ============

export interface SiteImage {
  src: string;
  alt: string;
  section: string;
  index: number;
}

export async function uploadMedia(siteId: number, file: File): Promise<{ url: string; filename: string }> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);
  formData.append("site_id", String(siteId));
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/api/media/upload`, {
    method: "POST",
    headers,
    body: formData,
  });
  return handleResponse<{ url: string; filename: string }>(res);
}

export async function getSiteImages(siteId: number): Promise<{ images: SiteImage[] }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/media/sites/${siteId}/images`, { headers });
  return handleResponse<{ images: SiteImage[] }>(res);
}

export async function replaceImage(siteId: number, oldSrc: string, newSrc: string): Promise<{ html_content: string; message: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/media/sites/${siteId}/replace-image`, {
    method: "PUT",
    headers,
    body: JSON.stringify({ old_src: oldSrc, new_src: newSrc }),
  });
  return handleResponse<{ html_content: string; message: string }>(res);
}

export async function addVideo(siteId: number, videoUrl: string, afterSection: string): Promise<{ html_content: string; message: string }> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/media/sites/${siteId}/add-video`, {
    method: "POST",
    headers,
    body: JSON.stringify({ video_url: videoUrl, after_section: afterSection }),
  });
  return handleResponse<{ html_content: string; message: string }>(res);
}

// ============ UTILS ============

/** Genera uno slug univoco dal nome */
export function generateSlug(name: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  const timestamp = Date.now().toString(36).slice(-4);
  return `${base}-${timestamp}`;
}
