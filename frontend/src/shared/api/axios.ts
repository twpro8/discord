// third party
import { isTauri } from "@tauri-apps/api/core";
import { fetch as tauriFetch } from "@tauri-apps/plugin-http";
import axios, { type AxiosRequestConfig } from "axios";

// relative
import { getApiBaseUrl } from "../config/backend";

/**
 * A built desktop app's webview loads bundled assets from Tauri's internal
 * origin (`tauri://localhost`, or `http://tauri.localhost` on Windows) —
 * a different site than whatever backend URL the user configures, so the
 * browser's SameSite cookie policy silently drops the auth cookie on every
 * cross-site request (and no cookie attribute can fix that for a plain-HTTP
 * self-hosted backend, since SameSite=None requires Secure/HTTPS). Routing
 * through Tauri's Rust-based HTTP client sidesteps this: its cookie jar
 * persists/resends cookies by domain/path/Secure like any plain HTTP
 * client, with no notion of "site" and no SameSite enforcement at all.
 * No-op in the web build, where `isTauri()` is false.
 */
const tauriAdapterConfig: Pick<AxiosRequestConfig, "adapter" | "env"> =
  isTauri() ? { adapter: "fetch", env: { fetch: tauriFetch } } : {};

/** Axios instance configured for the backend API with automatic 401 refresh. */
export const api = axios.create({
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
  ...tauriAdapterConfig,
});

api.interceptors.request.use((config) => {
  config.baseURL = `${getApiBaseUrl()}/api/v1`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await axios.post(
          `${getApiBaseUrl()}/api/v1/auth/refresh`,
          {},
          { withCredentials: true, ...tauriAdapterConfig },
        );
        return api(originalRequest);
      } catch {
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  },
);
