/** Backend API base URL, defaults to localhost:8000. Name must match the
 * `VITE_API_URL` build ARG declared in frontend/Dockerfile and passed by
 * both compose.yml and compose.override.yml — Vite only substitutes env
 * vars whose names match exactly. */
export const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ??
  "http://localhost:8000";

/** Backend WebSocket base URL, derived from the API URL unless overridden. */
export const WS_BASE_URL =
  (import.meta.env.VITE_WS_BASE_URL as string | undefined) ??
  API_BASE_URL.replace(/^http/, "ws");

/** Full WebSocket endpoint for the realtime event stream. */
export const WS_EVENTS_URL = `${WS_BASE_URL}/api/v1/ws`;

/** Reailtime Communication URL*/
export const CALL_SERVER_URL = 
  (import.meta.env.VITE_CALL_SERVER_URL as string | undefined) 
    ?? "ws://localhost:4000/socket";
