// shared
import { api } from "@/shared/api/axios";

// entities
import type { User } from "@/entities/user/model/types";

/** Uploads a new avatar for the current user. `Content-Type` is set to
 * `null` so the browser supplies the multipart boundary for the FormData
 * body instead of the instance's `application/json` default. */
export async function updateAvatar(file: File): Promise<User> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.put<User>("/users/me/avatar", formData, {
    headers: { "Content-Type": null },
  });
  return response.data;
}
