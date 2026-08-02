// shared
import { api } from "@/shared/api/axios";

// relative
import type { FriendRequestWithUser } from "../model/types";

/** Fetches the current user's friend list. */
export async function getFriends(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>("/friends");
  return response.data;
}
