/** Backend API base URL, defaults to localhost:8000. */
export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

/** Backend WebSocket base URL, derived from the API URL unless overridden. */
export const WS_BASE_URL =
  (import.meta.env.VITE_WS_BASE_URL as string | undefined) ??
  API_BASE_URL.replace(/^http/, "ws");

/** Full WebSocket endpoint for the realtime event stream. */
export const WS_EVENTS_URL = `${WS_BASE_URL}/api/v1/ws`;
