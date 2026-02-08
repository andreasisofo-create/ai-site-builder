/** Client API per comunicare con il backend */

// Usa path relativi per sfruttare il proxy Next.js -> Backend
// Il rewrite in next.config.js inoltra /api/* al backend
const API_BASE = "";  // Path relativi: "/api/..."

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
    // Se 401 Unauthorized, redirect al login
    if (res.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (typeof window !== "undefined") {
        window.location.href = "/auth";
      }
    }

    const error = await res.json().catch(() => ({ detail: "Errore sconosciuto" }));
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
  logo_url?: string;
}

export interface GenerateResponse {
  success: boolean;
  html_content?: string;
  model_used?: string;
  tokens_input?: number;
  tokens_output?: number;
  cost_usd?: number;
  generation_time_ms?: number;
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
