// shared
import { api } from "@/shared/api/axios";

// relative
import type { PrivateChatSummary } from "../model/types";

/** Fetches a private chat's details (including resolved peer identity). */
export async function getChatDetails(
  chatId: string,
): Promise<PrivateChatSummary> {
  const response = await api.get<PrivateChatSummary>(`/chats/${chatId}`);
  return response.data;
}
