// features
import type {
  CallBusyPayload,
  CallErrorPayload,
  CallHangupPayload,
  CallIceCandidatePayload,
  CallInvitePayload,
  CallMediaStatePayload,
  CallSdpPayload,
  CallSimplePayload,
} from "@/features/calls/model/types";
import type { ChatMessage } from "@/features/chats/model/types";
import type { PresenceEntry } from "@/features/presence/model/types";
import type { TypingUpdate } from "@/features/typing/model/types";

/** Events emitted by the backend realtime WebSocket. */
export type RealtimeEvent =
  | { type: "message.created"; payload: ChatMessage }
  | { type: "presence.update"; payload: PresenceEntry }
  | { type: "typing.update"; payload: TypingUpdate }
  | { type: "call.invite"; payload: CallInvitePayload }
  | { type: "call.accepted"; payload: CallSimplePayload }
  | { type: "call.rejected"; payload: CallSimplePayload }
  | { type: "call.cancelled"; payload: CallSimplePayload }
  | { type: "call.busy"; payload: CallBusyPayload }
  | { type: "call.timeout"; payload: CallSimplePayload }
  | { type: "call.hangup"; payload: CallHangupPayload }
  | { type: "call.offer"; payload: CallSdpPayload }
  | { type: "call.answer"; payload: CallSdpPayload }
  | { type: "call.ice_candidate"; payload: CallIceCandidatePayload }
  | { type: "call.media_state"; payload: CallMediaStatePayload }
  | { type: "error"; payload: CallErrorPayload };

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

/** Narrowing helper for call.invite events. */
export function isCallInviteEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.invite" }> {
  return event.type === "call.invite";
}

/** Narrowing helper for call.accepted events. */
export function isCallAcceptedEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.accepted" }> {
  return event.type === "call.accepted";
}

/** Narrowing helper for call.rejected events. */
export function isCallRejectedEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.rejected" }> {
  return event.type === "call.rejected";
}

/** Narrowing helper for call.cancelled events. */
export function isCallCancelledEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.cancelled" }> {
  return event.type === "call.cancelled";
}

/** Narrowing helper for call.busy events. */
export function isCallBusyEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.busy" }> {
  return event.type === "call.busy";
}

/** Narrowing helper for call.timeout events. */
export function isCallTimeoutEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.timeout" }> {
  return event.type === "call.timeout";
}

/** Narrowing helper for call.hangup events. */
export function isCallHangupEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.hangup" }> {
  return event.type === "call.hangup";
}

/** Narrowing helper for call.offer events. */
export function isCallOfferEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.offer" }> {
  return event.type === "call.offer";
}

/** Narrowing helper for call.answer events. */
export function isCallAnswerEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.answer" }> {
  return event.type === "call.answer";
}

/** Narrowing helper for call.ice_candidate events. */
export function isCallIceCandidateEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.ice_candidate" }> {
  return event.type === "call.ice_candidate";
}

/** Narrowing helper for call.media_state events. */
export function isCallMediaStateEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "call.media_state" }> {
  return event.type === "call.media_state";
}

/** Narrowing helper for the generic error event. */
export function isErrorEvent(
  event: RealtimeEvent,
): event is Extract<RealtimeEvent, { type: "error" }> {
  return event.type === "error";
}
