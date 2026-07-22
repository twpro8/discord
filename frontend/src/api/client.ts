import { client } from "@/client/client.gen";
import { ApiError } from "@/api/errors.ts";
import { ROUTES } from "@/routes.ts";

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json().catch(() => null);
    if (!data) return null;

    const newAccessToken = data.access_token;
    const newRefreshToken = data.refresh_token;

    if (newAccessToken) {
      localStorage.setItem("access_token", newAccessToken);
      if (newRefreshToken) {
        localStorage.setItem("refresh_token", newRefreshToken);
      }
      return newAccessToken;
    }

    return null;
  } catch {
    return null;
  }
}

function handleLogout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  if (window.location.pathname !== ROUTES.LOGIN) {
    window.location.replace(ROUTES.LOGIN);
  }
}

client.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    request.headers.set("Authorization", `Bearer ${token}`);
  }
  return request;
});

client.interceptors.response.use(async (response, request) => {
  if (response.ok) {
    return response;
  }

  const isRefreshUrl = request.url.includes("/auth/refresh");

  if (response.status === 401 && !isRefreshUrl) {
    const isRetry = request.headers.get("X-Is-Retry") === "true";

    if (!isRetry) {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newAccessToken = await refreshPromise;

      if (newAccessToken) {
        const retryRequest = request.clone();
        retryRequest.headers.set("Authorization", `Bearer ${newAccessToken}`);
        retryRequest.headers.set("X-Is-Retry", "true");

        return fetch(retryRequest);
      }
    }

    handleLogout();
    throw new ApiError(response.status, { message: "Unauthorized" });
  }

  const body = await response.json().catch(() => null);
  throw new ApiError(response.status, body);
});
