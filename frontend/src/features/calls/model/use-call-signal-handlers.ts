// third party
import { toast } from "sonner";

// relative
import type {
  CallBusyPayload,
  CallErrorPayload,
  CallHangupPayload,
  CallIceCandidatePayload,
  CallInvitePayload,
  CallMediaStatePayload,
  CallSdpPayload,
  CallSimplePayload,
} from "./types";
import { useCallStore } from "./use-call-store";
import {
  addRemoteIceCandidate,
  createAndSendOffer,
  handleRemoteAnswer,
  handleRemoteOffer,
  teardown,
} from "./webrtc-session";

/**
 * Pure functions routing inbound call.* / error realtime events into the
 * call store + webrtc-session — invoked from RealtimeProvider's
 * handleEvent, the same way mergeIncomingMessages/applyPresenceUpdate
 * are for their own event families.
 *
 * Every handler except handleCallInvite (which establishes it) first
 * checks the event's call_id against the store's own current callId —
 * the client-side half of the "late signaling can't resurrect an ended
 * call" invariant (see backend calls/application/call_signaling_service.py
 * and plan §2.8): an event for a call_id the client no longer considers
 * active is a no-op.
 */

export function handleCallInvite(
  payload: CallInvitePayload,
  selfUserId: string,
): void {
  if (payload.callee_id !== selfUserId) {
    // Echo of the caller's own outgoing invite, delivered to their other
    // tabs — the originating tab already set its own optimistic state in
    // use-start-call.ts, so there's nothing to do for a passive sibling
    // tab here (no local call state to protect, nothing to display but a
    // possible future "calling on another device" indicator).
    return;
  }
  useCallStore.getState().beginIncomingCall({
    callId: payload.call_id,
    chatId: payload.chat_id,
    peerId: payload.caller_id,
  });
}

export function handleCallAccepted(payload: CallSimplePayload): void {
  const state = useCallStore.getState();
  if (payload.call_id !== state.callId) return;

  if (state.direction === "outgoing") {
    useCallStore.getState().transitionToConnecting();
    void createAndSendOffer(payload.call_id);
    return;
  }
  if (state.phase === "incoming_ringing") {
    // This tab never sent call.accept itself (a sibling tab, or the
    // race-losing tab already told separately via call.busy) — dismiss.
    useCallStore.getState().reset();
  }
  // Otherwise this is the tab that itself accepted (already
  // "connecting"), which is a no-op confirmation.
}

function endRingingCall(callId: string): void {
  if (callId !== useCallStore.getState().callId) return;
  teardown();
  useCallStore.getState().reset();
}

export function handleCallRejected(payload: CallSimplePayload): void {
  endRingingCall(payload.call_id);
}

export function handleCallCancelled(payload: CallSimplePayload): void {
  endRingingCall(payload.call_id);
}

export function handleCallTimeout(payload: CallSimplePayload): void {
  endRingingCall(payload.call_id);
}

export function handleCallBusy(payload: CallBusyPayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  teardown();
  useCallStore.getState().reset();
  toast.error(busyMessage(payload.reason));
}

function busyMessage(reason: CallBusyPayload["reason"]): string {
  switch (reason) {
    case "self_busy":
      return "You're already on a call.";
    case "callee_busy":
      return "They're already on a call.";
    case "answered_elsewhere":
      return "Answered on another device.";
  }
}

export function handleCallHangup(payload: CallHangupPayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  teardown();
  useCallStore
    .getState()
    .endCall(payload.reason === "disconnected" ? "disconnected" : null);
}

export function handleCallOffer(payload: CallSdpPayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  void handleRemoteOffer(payload.call_id, payload.sdp);
}

export function handleCallAnswer(payload: CallSdpPayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  void handleRemoteAnswer(payload.sdp);
}

export function handleCallIceCandidate(payload: CallIceCandidatePayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  void addRemoteIceCandidate(payload.candidate);
}

export function handleCallMediaState(payload: CallMediaStatePayload): void {
  if (payload.call_id !== useCallStore.getState().callId) return;
  useCallStore
    .getState()
    .setPeerMediaState(payload.video_camera, payload.video_screen);
}

export function handleCallError(payload: CallErrorPayload): void {
  if (payload.call_id && payload.call_id !== useCallStore.getState().callId)
    return;
  teardown();
  useCallStore.getState().reset();
  toast.error(payload.message ?? "Couldn't start the call.");
}
