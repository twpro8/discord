// relative
import type { ChatMessage } from "@/features/chats/model/types";

/** Events emitted by the backend realtime WebSocket. */
export type RealtimeEvent = { type: "message.created"; payload: ChatMessage };

/** Narrowing helper for the events the client currently handles. */
export function isMessageCreatedEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "message.created" }> {
  return event.type === "message.created";
}
