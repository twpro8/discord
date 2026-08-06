// third party
import { create } from "zustand";

interface ShellDrawerState {
  isServersOpen: boolean;
  isChannelsOpen: boolean;
  isFriendsOpen: boolean;
  openServers: () => void;
  closeServers: () => void;
  toggleServers: () => void;
  openChannels: () => void;
  closeChannels: () => void;
  toggleChannels: () => void;
  openFriends: () => void;
  closeFriends: () => void;
  toggleFriends: () => void;
  closeAll: () => void;
}

/** Client state for the adaptive sidebar drawers, one open at a time. */
export const useShellDrawer = create<ShellDrawerState>()((set) => ({
  isServersOpen: false,
  isChannelsOpen: false,
  isFriendsOpen: false,
  openServers: () =>
    set({ isServersOpen: true, isChannelsOpen: false, isFriendsOpen: false }),
  closeServers: () => set({ isServersOpen: false }),
  toggleServers: () =>
    set((state) => ({
      isServersOpen: !state.isServersOpen,
      isChannelsOpen: false,
      isFriendsOpen: false,
    })),
  openChannels: () =>
    set({ isChannelsOpen: true, isServersOpen: false, isFriendsOpen: false }),
  closeChannels: () => set({ isChannelsOpen: false }),
  toggleChannels: () =>
    set((state) => ({
      isChannelsOpen: !state.isChannelsOpen,
      isServersOpen: false,
      isFriendsOpen: false,
    })),
  openFriends: () =>
    set({ isFriendsOpen: true, isServersOpen: false, isChannelsOpen: false }),
  closeFriends: () => set({ isFriendsOpen: false }),
  toggleFriends: () =>
    set((state) => ({
      isFriendsOpen: !state.isFriendsOpen,
      isServersOpen: false,
      isChannelsOpen: false,
    })),
  closeAll: () =>
    set({ isServersOpen: false, isChannelsOpen: false, isFriendsOpen: false }),
}));
