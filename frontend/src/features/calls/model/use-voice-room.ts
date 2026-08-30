// third party
import { create } from "zustand";

interface VoiceRoomState {
  channelId: string | null;
  roomId: string | null;
  join: (channelId: string) => void;
  leave: () => void;
}

/** Unified room for server voice channels: room:channel:{channelId} persistent.
 *  Joined without invite — join succeeds if user is server member (checked on call_server). */
export const useVoiceRoom = create<VoiceRoomState>()((set) => ({
  channelId: null,
  roomId: null,
  join: (channelId) => set({ channelId, roomId: `channel:${channelId}` }),
  leave: () => set({ channelId: null, roomId: null }),
}));
