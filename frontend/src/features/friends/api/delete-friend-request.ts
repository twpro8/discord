// shared
import { api } from "@/shared/api/axios";

/** Cancels or declines a friend request. */
export async function deleteFriendRequest(requestId: string): Promise<void> {
  await api.delete(`/friends/requests/${requestId}`);
}
