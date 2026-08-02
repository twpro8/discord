// third party
import { useQuery, type QueryClient } from "@tanstack/react-query";

// relative
import { getChatMessages } from "../api/get-chat-messages";
import { mergeChatMessages } from "./merge-chat-messages";
import type { ChatMessage } from "./types";

const messagesQueryKey = (chatId: string) => ["chat-messages", chatId] as const;

/**
 * Returns the messages for a chat. The realtime layer and the send
 * mutation write into the same cache via `mergeIncomingMessages`.
 */
export function useChatMessages(chatId: string) {
  return useQuery({
    queryKey: messagesQueryKey(chatId),
    queryFn: async () => {
      const page = await getChatMessages(chatId);
      return page.items;
    },
    staleTime: Infinity,
  });
}

/** Merges messages into the chat cache, deduplicating by id. */
export function mergeIncomingMessages(
  queryClient: QueryClient,
  chatId: string,
  messages: ChatMessage[],
) {
  queryClient.setQueryData<ChatMessage[]>(
    messagesQueryKey(chatId),
    (prev = []) => mergeChatMessages(prev, messages),
  );
}

/** Appends a single message to the chat cache. */
export function appendChatMessage(
  queryClient: QueryClient,
  chatId: string,
  message: ChatMessage,
) {
  mergeIncomingMessages(queryClient, chatId, [message]);
}
