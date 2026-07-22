import { client } from "@/client/client.gen";
import { ApiError } from "@/api/errors.ts";
import { ROUTES } from "@/routes.ts";

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
});

client.interceptors.request.use((request) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    request.headers.set("Authorization", `Bearer ${token}`)
  }
  return request
})

client.interceptors.response.use(async (response) => {
  if (response.ok) {
    return response
  }

  const body = await response.json().catch(() => null)

  if (response.status === 401) {
    localStorage.removeItem("access_token");
    if (window.location.pathname !== ROUTES.LOGIN) {
      window.location.replace(ROUTES.LOGIN);
    }
  }

  throw new ApiError(response.status, body)
})
