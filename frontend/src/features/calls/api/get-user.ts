// shared
import { api } from "@/shared/api/axios";

// entities
import type { User } from "@/entities/user/model/types";

/** Fetches a user's profile by id (GET /users/{id}). */
export async function getUserById(userId: string): Promise<User> {
  const response = await api.get<User>(`/users/${userId}`);
  return response.data;
}
