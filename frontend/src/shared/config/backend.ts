import { API_BASE_URL, WS_EVENTS_URL } from "./env";

const STORAGE_KEY = "lumiere.backend-url";

type ParseResult = { ok: true; value: string } | { ok: false; error: string };

/** Validates and normalizes a user-supplied backend origin to a bare `scheme://host[:port]` string. */
export function parseBackendUrl(value: string): ParseResult {
  const trimmed = value.trim();
  if (!trimmed) {
    return { ok: false, error: "Server URL is required." };
  }

  let url: URL;
  try {
    url = new URL(trimmed);
  } catch {
    return {
      ok: false,
      error: "Enter a valid URL, e.g. https://your-server.example.com.",
    };
  }

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return { ok: false, error: "Server URL must use http or https." };
  }

  if (url.pathname.replace(/\/+$/, "") !== "" || url.search || url.hash) {
    return {
      ok: false,
      error:
        "Server URL must be a plain address with no path, query, or fragment.",
    };
  }

  return { ok: true, value: url.origin };
}

/** Reads the locally-persisted backend override, if any and still valid. */
export function readBackendUrlOverride(): string | null {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (!stored) return null;

  const result = parseBackendUrl(stored);
  return result.ok ? result.value : null;
}

/** Validates and persists a backend override, replacing whatever is currently stored. */
export function saveBackendUrlOverride(value: string): ParseResult {
  const result = parseBackendUrl(value);
  if (!result.ok) return result;

  window.localStorage.setItem(STORAGE_KEY, result.value);
  return result;
}

/** Removes the local override, reverting to the build-time default. */
export function clearBackendUrlOverride() {
  window.localStorage.removeItem(STORAGE_KEY);
}

/** The API origin to use right now: the local override if set, else the build-time default. */
export function getApiBaseUrl(): string {
  return readBackendUrlOverride() ?? API_BASE_URL;
}

/** The realtime WebSocket endpoint to use right now, derived from the same origin as {@link getApiBaseUrl}. */
export function getWsEventsUrl(): string {
  const override = readBackendUrlOverride();
  if (!override) return WS_EVENTS_URL;

  const wsUrl = new URL(override);
  wsUrl.protocol = wsUrl.protocol === "https:" ? "wss:" : "ws:";
  return `${wsUrl.origin}/api/v1/ws`;
}
