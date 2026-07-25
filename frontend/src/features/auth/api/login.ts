import { api } from '@/shared/api/axios'

export interface LoginCredentials {
  username: string
  password: string
}

export async function loginUser(username: string, password: string): Promise<void> {
  await api.post('/auth/login', { username, password }, {
    headers: { 'Content-Type': 'application/json', },
  })
}
