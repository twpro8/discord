// relative
import type { ChatMessage } from "./types";

/**
 * Merges incoming messages into an existing list, deduplicating by id and
 * keeping messages sorted chronologically. The incoming list wins on id
 * conflicts (server/realtime data is fresher than the optimistic copy).
 */
export function mergeChatMessages(
  existing: ChatMessage[],
  incoming: ChatMessage[],
): ChatMessage[] {
  if (incoming.length === 0) return existing;

  const byId = new Map<string, ChatMessage>();
  for (const message of existing) {
    byId.set(message.id, message);
  }
  for (const message of incoming) {
    byId.set(message.id, message);
  }

  return [...byId.values()].sort(
    (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  );
}
