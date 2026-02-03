/** Client API per comunicare con il backend */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchSites() {
  const res = await fetch(`${API_BASE}/api/sites/`);
  if (!res.ok) throw new Error("Errore nel caricamento siti");
  return res.json();
}

export async function createSite(name: string, slug: string) {
  const res = await fetch(`${API_BASE}/api/sites/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ name, slug }),
  });
  if (!res.ok) throw new Error("Errore nella creazione");
  return res.json();
}

export async function getSite(id: number) {
  const res = await fetch(`${API_BASE}/api/sites/${id}`);
  if (!res.ok) throw new Error("Sito non trovato");
  return res.json();
}

export async function updateSite(id: number, data: Partial<{ name: string; config: object }>) {
  const params = new URLSearchParams();
  if (data.name) params.append("name", data.name);
  if (data.config) params.append("config", JSON.stringify(data.config));
  
  const res = await fetch(`${API_BASE}/api/sites/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params,
  });
  if (!res.ok) throw new Error("Errore nell'aggiornamento");
  return res.json();
}

export async function fetchComponents(siteId: number) {
  const res = await fetch(`${API_BASE}/api/components/site/${siteId}`);
  if (!res.ok) throw new Error("Errore nel caricamento componenti");
  return res.json();
}

export async function createComponent(
  siteId: number,
  name: string,
  type: string,
  content?: object,
  styles?: object
) {
  const params = new URLSearchParams({ site_id: String(siteId), name, type });
  if (content) params.append("content", JSON.stringify(content));
  if (styles) params.append("styles", JSON.stringify(styles));
  
  const res = await fetch(`${API_BASE}/api/components/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params,
  });
  if (!res.ok) throw new Error("Errore nella creazione componente");
  return res.json();
}
