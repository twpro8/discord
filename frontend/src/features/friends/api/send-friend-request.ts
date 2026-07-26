import { api } from '@/shared/api/axios'

export interface SendFriendRequestInput {
  username: string
}

export async function sendFriendRequest(input: SendFriendRequestInput): Promise<void> {
  await api.post('/friends/requests', input)
}
