// shared
import { api } from "@/shared/api/axios";

// entities
import type { User } from "@/entities/user/model/types";

export interface UpdateProfilePayload {
  name?: string;
  username?: string;
  email?: string;
}

/** Patches the current user's profile fields. */
export async function updateProfile(
  payload: UpdateProfilePayload,
): Promise<User> {
  const response = await api.patch<User>("/users/me", payload);
  return response.data;
}
