// shared
import { api } from "@/shared/api/axios";

// relative
import type { FriendRequestWithUser } from "../model/types";

/** Fetches outgoing friend requests. */
export async function getSentRequests(): Promise<FriendRequestWithUser[]> {
  const response = await api.get<FriendRequestWithUser[]>(
    "/friends/requests/sent",
  );
  return response.data;
}
