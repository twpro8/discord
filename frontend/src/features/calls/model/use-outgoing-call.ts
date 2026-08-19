// third party
import { create } from "zustand";

interface OutgoingCallState {
  peerId: string | null;
  open: (peerId: string) => void;
  clear: () => void;
}

/** Client state for the caller's outgoing-call window, opened from the
 * deep CallButton and rendered by HomeLayout. */
export const useOutgoingCall = create<OutgoingCallState>()((set) => ({
  peerId: null,
  open: (peerId) => set({ peerId }),
  clear: () => set({ peerId: null }),
}));
