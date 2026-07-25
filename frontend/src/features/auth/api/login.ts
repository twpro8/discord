import { api } from '@/shared/api/axios'
import type { TokenPair } from '@/shared/api/types'

export interface LoginCredentials {
  username: string
  password: string
}

export async function loginUser(username: string, password: string): Promise<TokenPair> {
  const formData = new URLSearchParams({ username, password })
  const response = await api.post<TokenPair>('/auth/login', formData.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}
