// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getChatDetails } from "../api/get-chat-details";

/**
 * Authoritative chat details (peer identity, for private chats) — the
 * source of truth for who the peer is, independent of how the user
 * navigated here. A chat's peer never changes, so this never needs to
 * refetch once loaded.
 *
 * `chatId` accepts `null`/`undefined` for callers that are always
 * mounted regardless of whether a chat is currently relevant (e.g. the
 * global call overlay) — the query is disabled rather than firing
 * against an invalid id.
 */
export function useChatDetails(chatId: string | null | undefined) {
  return useQuery({
    queryKey: ["chat-details", chatId],
    queryFn: () => getChatDetails(chatId ?? ""),
    enabled: Boolean(chatId),
    staleTime: Infinity,
  });
}
