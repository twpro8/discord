// third party
import { useShallow } from "zustand/react/shallow";

// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { useTypingStore } from "./use-typing-store";

/**
 * User ids currently typing in `chatId`, excluding the current user —
 * self-typing-events must be filtered client-side (the server has no
 * notion of "the viewer"; it just relays to the whole room, including the
 * sender's own other connections).
 *
 * Wrapped in `useShallow`: the selector builds a fresh array on every
 * call (`Object.keys(...).filter(...)`), and without shallow-memoizing
 * that output, React's `useSyncExternalStore` (which Zustand's hook uses
 * internally) sees a new reference on every render check, decides the
 * store "changed" again, and loops — surfacing as a real "Maximum update
 * depth exceeded" crash, not just an avoidable extra render.
 */
export function useTypingUsers(chatId: string): string[] {
  const { data: user } = useCurrentUser();
  return useTypingStore(
    useShallow((state) =>
      Object.keys(state.typingByChat[chatId] ?? {}).filter(
        (id) => id !== user?.id,
      ),
    ),
  );
}
