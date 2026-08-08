// features
import type { ChatMessage } from "@/features/chats/model/types";
import type { PresenceEntry } from "@/features/presence/model/types";
import type { TypingUpdate } from "@/features/typing/model/types";

/** Events emitted by the backend realtime WebSocket. */
export type RealtimeEvent =
  | { type: "message.created"; payload: ChatMessage }
  | { type: "presence.update"; payload: PresenceEntry }
  | { type: "typing.update"; payload: TypingUpdate };

/** Narrowing helper for the events the client currently handles. */
export function isMessageCreatedEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "message.created" }> {
  return event.type === "message.created";
}

/** Narrowing helper for presence.update events. */
export function isPresenceUpdateEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "presence.update" }> {
  return event.type === "presence.update";
}

/** Narrowing helper for typing.update events. */
export function isTypingUpdateEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "typing.update" }> {
  return event.type === "typing.update";
}
