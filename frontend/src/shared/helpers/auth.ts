// shared
import { api } from "@/shared/api/axios";

/** Checks if the current session is authenticated by calling GET /users/me. */
export async function checkAuth(): Promise<boolean> {
  try {
    await api.get("/users/me");
    return true;
  } catch {
    return false;
  }
}

/** Clears auth cookies, effectively logging the user out. */
export function clearAuthState(): void {
  document.cookie = "access_token=; Max-Age=0; path=/";
  document.cookie = "refresh_token=; Max-Age=0; path=/";
}
