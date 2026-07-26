import { api } from '@/shared/api/axios'
import type { FriendRequestWithUser } from '../model/types'

export async function getFriendRequests(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>('/friends/requests')
  return response.data
}
