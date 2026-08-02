// shared
import { api } from "@/shared/api/axios";

// relative
import type { PrivateChatSummary } from "../model/types";

/**
 * Creates a private chat with a peer, or returns the existing one if a
 * conversation already exists between the two users.
 */
export async function createPrivateChat(
  targetUserId: string,
): Promise<PrivateChatSummary> {
  const response = await api.post<PrivateChatSummary>("/chats", {
    type: "private",
    target_user_id: targetUserId,
  });
  return response.data;
}
