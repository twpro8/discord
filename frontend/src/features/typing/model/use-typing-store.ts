// third party
import { create } from "zustand";

// Comfortably above use-send-typing's ~2.5s throttle so one or two
// delayed/dropped frames don't cause visible flicker, short enough that a
// crashed tab's indicator clears promptly.
const AUTO_EXPIRE_MS = 7_000;

// Timer handles are bookkeeping, not render-relevant data — kept out of
// Zustand state (which should only ever hold what's rendered).
const timeoutHandles = new Map<string, ReturnType<typeof setTimeout>>();
const timeoutKey = (chatId: string, userId: string) => `${chatId}:${userId}`;

interface TypingState {
  typingByChat: Record<string, Record<string, true>>;
  applyTypingUpdate: (
    chatId: string,
    userId: string,
    isTyping: boolean,
  ) => void;
}

function removeTyping(chatId: string, userId: string) {
  useTypingStore.setState((state) => {
    const chatEntry = state.typingByChat[chatId];
    if (!chatEntry?.[userId]) return state;
    const next = { ...chatEntry };
    delete next[userId];
    return { typingByChat: { ...state.typingByChat, [chatId]: next } };
  });
}

/** Client-only, WS-originated typing state — no REST source of truth to
 * reconcile against, so unlike messages/presence this isn't a query cache. */
export const useTypingStore = create<TypingState>()((set) => ({
  typingByChat: {},
  applyTypingUpdate: (chatId, userId, isTyping) => {
    const key = timeoutKey(chatId, userId);
    const existing = timeoutHandles.get(key);
    if (existing) clearTimeout(existing);
    timeoutHandles.delete(key);

    if (!isTyping) {
      removeTyping(chatId, userId);
      return;
    }

    timeoutHandles.set(
      key,
      setTimeout(() => {
        timeoutHandles.delete(key);
        removeTyping(chatId, userId);
      }, AUTO_EXPIRE_MS),
    );

    set((state) => ({
      typingByChat: {
        ...state.typingByChat,
        [chatId]: { ...state.typingByChat[chatId], [userId]: true },
      },
    }));
  },
}));
