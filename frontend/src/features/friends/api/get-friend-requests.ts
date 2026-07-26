// shared
import { api } from "@/shared/api/axios";

// relative
import type { FriendRequestWithUser } from "../model/types";

/** Fetches incoming friend requests. */
export async function getFriendRequests(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>("/friends/requests");
  return response.data;
}
