// third party
import { create } from "zustand";

interface OutgoingCallState {
  peerId: string | null;
  callId: string | null;
  roomId: string | null;
  acceptedCallId: string | null;
  acceptedRoomId: string | null;
  participantIds: string[] | null;
  open: (peerId: string, callId: string) => void;
  openRoom: (roomId: string, participantIds: string[]) => void;
  setAccepted: (callId: string) => void;
  clear: () => void;
}

/** Client state for the caller's outgoing-call window. Unified room for
 *  1:1/group/server voice. `callId` kept as alias for `roomId`. */
export const useOutgoingCall = create<OutgoingCallState>()((set) => ({
  peerId: null,
  callId: null,
  roomId: null,
  acceptedCallId: null,
  acceptedRoomId: null,
  participantIds: null,
  open: (peerId, callId) =>
    set({
      peerId,
      callId,
      roomId: callId,
      participantIds: [peerId],
      acceptedCallId: null,
      acceptedRoomId: null,
    }),
  openRoom: (roomId, participantIds) =>
    set({
      peerId: participantIds[0] ?? null,
      callId: roomId,
      roomId,
      participantIds,
      acceptedCallId: null,
      acceptedRoomId: null,
    }),
  setAccepted: (callId) =>
    set({ acceptedCallId: callId, acceptedRoomId: callId }),
  clear: () =>
    set({
      peerId: null,
      callId: null,
      roomId: null,
      participantIds: null,
      acceptedCallId: null,
      acceptedRoomId: null,
    }),
}));
