import { getSession } from "next-auth/react";

/**
 * Ottiene il token JWT del backend per le chiamate API
 */
export async function getBackendToken(): Promise<string | null> {
  const session = await getSession();
  return (session as any)?.backendToken || null;
}

/**
 * Headers per chiamate API autenticate
 */
export async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await getBackendToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * Fetch autenticato verso il backend
 */
export async function authFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = await getAuthHeaders();
  
  return fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers || {}),
    },
  });
}
