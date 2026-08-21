// third party
import { create } from "zustand";

interface OutgoingCallState {
  peerId: string | null;
  callId: string | null;
  acceptedCallId: string | null;
  open: (peerId: string, callId: string) => void;
  setAccepted: (callId: string) => void;
  clear: () => void;
}

/** Client state for the caller's outgoing-call window, opened from the
 * deep CallButton and rendered by HomeLayout. `acceptedCallId` is set
 * when the callee accepts, triggering WebRTC connection setup. */
export const useOutgoingCall = create<OutgoingCallState>()((set) => ({
  peerId: null,
  callId: null,
  acceptedCallId: null,
  open: (peerId, callId) => set({ peerId, callId, acceptedCallId: null }),
  setAccepted: (callId) => set({ acceptedCallId: callId }),
  clear: () => set({ peerId: null, callId: null, acceptedCallId: null }),
}));
