import { api } from '@/shared/api/axios'

export async function deleteFriendRequest(requestId: string): Promise<void> {
  await api.delete(`/friends/requests/${requestId}`)
}
