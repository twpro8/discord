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

  endCall: (errorMessage = null) => {
    set((state) => ({
      ...state,
      phase: "ended",
      errorMessage,
      localStream: null,
      remoteStream: null,
    }));
  },

  reset: () => {
    set({ ...INITIAL_STATE });
  },
}));
