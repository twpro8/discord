import { api } from '@/shared/api/axios'

export async function checkAuth(): Promise<boolean> {
  try {
    await api.get('/users/me')
    return true
  } catch {
    return false
  }
}

export function clearAuthState(): void {
  document.cookie = 'access_token=; Max-Age=0; path=/'
  document.cookie = 'refresh_token=; Max-Age=0; path=/'
}
