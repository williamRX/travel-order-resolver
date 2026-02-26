/**
 * URL de base de l'API (alignée sur frontend/index.html).
 * En dev sur localhost, utiliser http://localhost:8000 ; en Docker, le front peut appeler api:8000.
 */
const API_BASE =
  typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL
    ? import.meta.env.VITE_API_URL
    : "http://localhost:8000";

export function getApiBase(): string {
  return API_BASE;
}
