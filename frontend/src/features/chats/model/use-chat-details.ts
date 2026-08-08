// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getChatDetails } from "../api/get-chat-details";

/**
 * Authoritative chat details (peer identity, for private chats) — the
 * source of truth for who the peer is, independent of how the user
 * navigated here. A chat's peer never changes, so this never needs to
 * refetch once loaded.
 */
export function useChatDetails(chatId: string) {
  return useQuery({
    queryKey: ["chat-details", chatId],
    queryFn: () => getChatDetails(chatId),
    staleTime: Infinity,
  });
}
