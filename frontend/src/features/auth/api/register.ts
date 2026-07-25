import { api } from '@/shared/api/axios'
import type { User } from '@/entities/user/model/types'

export interface RegisterForm {
  name: string
  username: string
  email: string
  password: string
}

export async function registerUser(data: RegisterForm): Promise<User> {
  const response = await api.post<User>('/auth/register', data)
  return response.data
}
