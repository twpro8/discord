// shared
import { api } from "@/shared/api/axios";

/** Accepts an incoming friend request. */
export async function acceptFriendRequest(requestId: string): Promise<void> {
  await api.patch(`/friends/requests/${requestId}/accept`);
}
