// shared
import { api } from "@/shared/api/axios";

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

/** Changes the current user's password. */
export async function changePassword(
  payload: ChangePasswordPayload,
): Promise<void> {
  await api.post("/users/me/password", payload);
}
