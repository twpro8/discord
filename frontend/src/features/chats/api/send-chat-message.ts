// shared
import { api } from "@/shared/api/axios";

// relative
import type { ChatMessage } from "../model/types";

/** Sends a message to a chat and returns the persisted message. */
export async function sendChatMessage(
  chatId: string,
  body: string,
): Promise<ChatMessage> {
  const response = await api.post<ChatMessage>(`/chats/${chatId}/messages`, {
    body,
  });
  return response.data;
}
