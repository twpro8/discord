// third party
import { create } from "zustand";

interface ShellDrawerState {
  isServersOpen: boolean;
  isFriendsOpen: boolean;
  openServers: () => void;
  closeServers: () => void;
  toggleServers: () => void;
  openFriends: () => void;
  closeFriends: () => void;
  toggleFriends: () => void;
  closeAll: () => void;
}

/** Client state for the adaptive sidebar drawers, one open at a time. */
export const useShellDrawer = create<ShellDrawerState>()((set) => ({
  isServersOpen: false,
  isFriendsOpen: false,
  openServers: () => set({ isServersOpen: true, isFriendsOpen: false }),
  closeServers: () => set({ isServersOpen: false }),
  toggleServers: () =>
    set((state) => ({
      isServersOpen: !state.isServersOpen,
      isFriendsOpen: false,
    })),
  openFriends: () => set({ isFriendsOpen: true, isServersOpen: false }),
  closeFriends: () => set({ isFriendsOpen: false }),
  toggleFriends: () =>
    set((state) => ({
      isFriendsOpen: !state.isFriendsOpen,
      isServersOpen: false,
    })),
  closeAll: () => set({ isServersOpen: false, isFriendsOpen: false }),
}));
