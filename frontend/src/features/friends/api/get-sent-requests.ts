import { api } from '@/shared/api/axios'
import type { FriendRequestWithUser } from '../model/types'

export async function getSentRequests(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>('/friends/requests/sent')
  return response.data
}
