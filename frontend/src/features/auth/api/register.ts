// shared
import { api } from "@/shared/api/axios";

// entities
import type { User } from "@/entities/user/model/types";

/** Registration form data. */
export interface RegisterForm {
  name: string;
  username: string;
  email: string;
  password: string;
}

/** Registers a new user account and returns the user. */
export async function registerUser(data: RegisterForm): Promise<User> {
  const response = await api.post<User>("/auth/register", data);
  return response.data;
}
