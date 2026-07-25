import { api } from '@/shared/api/axios'
import type { User } from '@/entities/user'

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/users/me')
  return response.data
}
