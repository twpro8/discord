/** Client-side call lifecycle. Mirrors the backend's CallState (ringing |
 * active) plus the states that only ever exist on the client: the two
 * "who initiated this" ringing variants, connecting (accepted, waiting
 * on WebRTC negotiation), and ended (a brief terminal display state
 * before resetting to idle). */
export type CallPhase =
  | "idle"
  | "outgoing_ringing"
  | "incoming_ringing"
  | "connecting"
  | "active"
  | "ended";

/** Aligned with the backend's call.invite WS event payload. */
export interface CallInvitePayload {
  call_id: string;
  chat_id: string;
  caller_id: string;
  callee_id: string;
}

/** Aligned with call.accepted / call.rejected / call.cancelled / call.timeout. */
export interface CallSimplePayload {
  call_id: string;
}

/** Aligned with the backend's call.busy WS event payload. */
export interface CallBusyPayload {
  call_id: string;
  reason: "callee_busy" | "self_busy" | "answered_elsewhere";
}

/** Aligned with the backend's call.hangup WS event payload. */
export interface CallHangupPayload {
  call_id: string;
  reason: "hangup" | "disconnected";
}

/** Aligned with call.offer / call.answer — the server never parses `sdp`,
 * it's relayed opaquely end to end. */
export interface CallSdpPayload {
  call_id: string;
  sdp: RTCSessionDescriptionInit;
}

/** Aligned with the backend's call.ice_candidate WS event payload. */
export interface CallIceCandidatePayload {
  call_id: string;
  candidate: RTCIceCandidateInit;
}

/** Aligned with the backend's call.media_state WS event payload — the
 * peer's live camera/screen share state, relayed verbatim like SDP.
 * Future media toggles (mic mute, device changes) extend this payload
 * without touching the backend relay. */
export interface CallMediaStatePayload {
  call_id: string;
  video_camera: boolean;
  video_screen: boolean;
}

/** Aligned with the backend's generic `error` WS event payload — calls is
 * currently the only feature that surfaces this event type. */
export interface CallErrorPayload {
  call_id?: string;
  code: string;
  message?: string;
}

/** Response shape of GET /calls/turn-credentials — the single source of
 * ICE server config; the frontend has none of its own. */
export interface IceServersResponse {
  ice_servers: RTCIceServer[];
}
