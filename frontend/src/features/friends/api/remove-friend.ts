import { api } from '@/shared/api/axios'

export async function removeFriend(relationshipId: string): Promise<void> {
  await api.delete(`/friends/${relationshipId}`)
}
