// third party
import { create } from "zustand";

// relative
import type { CallPhase } from "./types";

interface CallStoreState {
  phase: CallPhase;
  callId: string | null;
  chatId: string | null;
  peerId: string | null;
  peerName: string | null;
  direction: "outgoing" | "incoming" | null;
  isMuted: boolean;
  /** A local camera/display video track is being sent to the peer (added
   * mid-call via webrtc-session.ts's startCameraShare/startScreenShare —
   * calls themselves stay voice-only, video is opted into per-call). */
  isSharingVideo: boolean;
  isScreenSharing: boolean;
  /** The peer's camera/screen share state as reported over signaling
   * (call.media_state) — the authoritative "peer is/stopped sharing"
   * signal. The peer's remote track muting fires no reliable event on
   * stop, so the overlay's collapse must come from here, not tracks. */
  peerIsSharingVideo: boolean;
  peerIsScreenSharing: boolean;
  errorMessage: string | null;
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;

  beginOutgoingCall: (args: {
    callId: string;
    chatId: string;
    peerId: string;
    peerName: string;
    localStream: MediaStream;
  }) => void;
  beginIncomingCall: (args: {
    callId: string;
    chatId: string;
    peerId: string;
    /** The call.invite WS payload carries ids only — a display name isn't
     * always available yet at invite time. UI components should prefer
     * resolving it reactively via useChatDetails(chatId), the same
     * peer_name-from-chat-details pattern DmChatView already uses,
     * falling back to this if provided. */
    peerName?: string | null;
  }) => void;
  transitionToConnecting: (localStream?: MediaStream) => void;
  transitionToActive: (remoteStream: MediaStream) => void;
  toggleMute: () => void;
  /** Set by webrtc-session.ts when a camera/screen track starts or stops
   * being sent — mirrors the store's non-renderable-object rule: the
   * streams themselves live outside Zustand, only these renderable
   * booleans cross it. */
  setSharingVideo: (sharing: boolean) => void;
  setSharingScreen: (sharing: boolean) => void;
  /** Set by handleCallMediaState on call.media_state — mirrors the
   * peer's own setSharingVideo/setSharingScreen onto THIS client. */
  setPeerMediaState: (videoCamera: boolean, videoScreen: boolean) => void;
  /** Post-media-negotiation ending — briefly shows an "ended" state
   * (see ActiveCallOverlay's auto-reset) before the caller resets to
   * idle. Use `reset()` directly for pre-media endings (reject/cancel/
   * busy/timeout while still ringing), which have no media to visibly
   * tear down. */
  endCall: (errorMessage?: string | null) => void;
  reset: () => void;
}

const INITIAL_STATE = {
  phase: "idle" as CallPhase,
  callId: null,
  chatId: null,
  peerId: null,
  peerName: null,
  direction: null,
  isMuted: false,
  isSharingVideo: false,
  isScreenSharing: false,
  peerIsSharingVideo: false,
  peerIsScreenSharing: false,
  errorMessage: null,
  localStream: null,
  remoteStream: null,
};

/** Client-only, WS-originated call lifecycle state — no REST source of
 * truth to reconcile against, so (like typing) this isn't a query cache.
 * The RTCPeerConnection itself is deliberately NOT stored here (not
 * renderable data) — see webrtc-session.ts, which keeps it as a
 * module-level variable the same way socket-sender.ts keeps the raw
 * WebSocket's send function outside any store. */
export const useCallStore = create<CallStoreState>()((set) => ({
  ...INITIAL_STATE,

  beginOutgoingCall: ({ callId, chatId, peerId, peerName, localStream }) => {
    set({
      ...INITIAL_STATE,
      phase: "outgoing_ringing",
      callId,
      chatId,
      peerId,
      peerName,
      direction: "outgoing",
      localStream,
    });
  },

  beginIncomingCall: ({ callId, chatId, peerId, peerName }) => {
    set({
      ...INITIAL_STATE,
      phase: "incoming_ringing",
      callId,
      chatId,
      peerId,
      peerName: peerName ?? null,
      direction: "incoming",
    });
  },

  transitionToConnecting: (localStream) => {
    set((state) => ({
      phase: "connecting",
      localStream: localStream ?? state.localStream,
    }));
  },

  transitionToActive: (remoteStream) => {
    set({ phase: "active", remoteStream });
  },

  toggleMute: () => {
    set((state) => ({ isMuted: !state.isMuted }));
  },

  setSharingVideo: (sharing) => {
    set({ isSharingVideo: sharing });
  },

  setSharingScreen: (sharing) => {
    set({ isScreenSharing: sharing });
  },

  setPeerMediaState: (videoCamera, videoScreen) => {
    set({ peerIsSharingVideo: videoCamera, peerIsScreenSharing: videoScreen });
  },

  endCall: (errorMessage = null) => {
    set((state) => ({
      ...state,
      phase: "ended",
      errorMessage,
      localStream: null,
      remoteStream: null,
      peerIsSharingVideo: false,
      peerIsScreenSharing: false,
    }));
  },

  reset: () => {
    set({ ...INITIAL_STATE });
  },
}));
