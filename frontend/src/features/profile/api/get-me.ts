// shared
import { api } from "@/shared/api/axios";

// entities
import type { User } from "@/entities/user/model/types";

/** Fetches the currently authenticated user's profile. */
export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/users/me");
  return response.data;
}
