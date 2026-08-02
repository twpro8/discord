// shared
import { api } from "@/shared/api/axios";

/** Credentials for user login. */
export interface LoginCredentials {
  username: string;
  password: string;
}

/** Authenticates a user and sets session cookies. */
export async function loginUser(
  username: string,
  password: string,
): Promise<void> {
  await api.post(
    "/auth/login",
    { username, password },
    {
      headers: { "Content-Type": "application/json" },
    },
  );
}
