import { api } from '@/shared/api/axios'
import type { FriendRequestWithUser } from '../model/types'

export async function getFriends(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>('/friends')
  return response.data
}
