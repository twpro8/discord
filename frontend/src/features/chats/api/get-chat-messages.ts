// shared
import { api } from "@/shared/api/axios";

// relative
import type { ChatMessagePage } from "../model/types";

/** Fetches a page of messages for a chat, newest first from the API. */
export async function getChatMessages(
  chatId: string,
  params?: { limit?: number; before_cursor?: string },
): Promise<ChatMessagePage> {
  const response = await api.get<ChatMessagePage>(`/chats/${chatId}/messages`, {
    params,
  });
  return response.data;
}
