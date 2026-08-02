// react
import { useEffect, type ReactNode } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";

// shared
import { WS_EVENTS_URL } from "@/shared/config/env";

// features
import { mergeIncomingMessages } from "@/features/chats/model/use-chat-messages";
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { isMessageCreatedEvent, type RealtimeEvent } from "./types";

const MAX_RETRY_MS = 30_000;
const INITIAL_RETRY_MS = 1_000;

/**
 * Maintains a single WebSocket connection to the backend event stream
 * while the current user is authenticated, reconnecting with backoff on
 * drops. Incoming `message.created` events are merged into the matching
 * chat-messages cache.
 */
export function RealtimeProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();
  const userId = user?.id;

  useEffect(() => {
    if (!userId) return;

    let socket: WebSocket | null = null;
    let retryMs = INITIAL_RETRY_MS;
    let retryTimer: number | undefined;
    let disposed = false;

    const handleEvent = (event: MessageEvent<string>) => {
      let parsed: RealtimeEvent;
      try {
        parsed = JSON.parse(event.data) as RealtimeEvent;
      } catch {
        return;
      }

      if (isMessageCreatedEvent(parsed)) {
        const message = parsed.payload;
        mergeIncomingMessages(queryClient, message.chat_id, [message]);
      }
    };

    const connect = () => {
      socket = new WebSocket(WS_EVENTS_URL);
      socket.onopen = () => {
        retryMs = INITIAL_RETRY_MS;
      };
      socket.onmessage = handleEvent;
      socket.onerror = () => socket?.close();
      socket.onclose = () => {
        if (disposed) return;
        retryTimer = window.setTimeout(() => {
          retryMs = Math.min(retryMs * 2, MAX_RETRY_MS);
          connect();
        }, retryMs);
      };
    };

    connect();

    return () => {
      disposed = true;
      window.clearTimeout(retryTimer);
      socket?.close();
    };
  }, [userId, queryClient]);

  return <>{children}</>;
}
