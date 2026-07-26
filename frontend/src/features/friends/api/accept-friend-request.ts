import { api } from '@/shared/api/axios'

export async function acceptFriendRequest(requestId: string): Promise<void> {
  await api.patch(`/friends/requests/${requestId}/accept`)
}
