import { client } from "@/client/client.gen";
import { ApiError } from "@/api/errors.ts";

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
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body)
  }
  return response
})
