// react
import { useEffect, useRef } from "react";

// features
import { socketSend } from "@/features/realtime/model/socket-sender";

// Leading-edge throttle: sends at most once per this interval while the
// user keeps typing, rather than on every keystroke.
const THROTTLE_MS = 2_500;

/** Sends `typing` frames for `chatId` over the realtime socket, throttled
 * while actively typing and with an explicit immediate stop. */
export function useSendTyping(chatId: string) {
  const lastSentAtRef = useRef(0);
  const isTypingRef = useRef(false);
  const chatIdRef = useRef(chatId);
  chatIdRef.current = chatId;

  const notifyStopTyping = () => {
    if (!isTypingRef.current) return;
    isTypingRef.current = false;
    lastSentAtRef.current = 0;
    socketSend({
      type: "typing",
      chat_id: chatIdRef.current,
      is_typing: false,
    });
  };

  const notifyTyping = () => {
    const now = Date.now();
    isTypingRef.current = true;
    if (now - lastSentAtRef.current < THROTTLE_MS) return;
    lastSentAtRef.current = now;
    socketSend({ type: "typing", chat_id: chatIdRef.current, is_typing: true });
  };

  // Fire an explicit stop when switching chats or unmounting (e.g.
  // navigating away mid-composition) — belt-and-suspenders on top of the
  // receiver's own auto-expiry timer, so peers don't wait out the full
  // auto-expiry window for the common "closed the chat" case.
  useEffect(() => {
    return () => notifyStopTyping();
  }, [chatId]);

  return { notifyTyping, notifyStopTyping };
}
