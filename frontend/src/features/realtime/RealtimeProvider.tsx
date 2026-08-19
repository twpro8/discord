// react
import { useEffect, useRef, type ReactNode } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";

// shared
import { getWsEventsUrl } from "@/shared/config/backend";

// features
import { mergeIncomingMessages } from "@/features/chats/model/use-chat-messages";
import { applyPresenceUpdate } from "@/features/presence/model/apply-presence-update";
import { useCurrentUser } from "@/features/profile/model/use-current-user";
import { useTypingStore } from "@/features/typing/model/use-typing-store";

// relative
import { setSocketSend } from "./model/socket-sender";
import { useIdle } from "./model/use-idle";
import {
  isMessageCreatedEvent,
  isPresenceUpdateEvent,
  isTypingUpdateEvent,
  type RealtimeEvent,
} from "./types";

const MAX_RETRY_MS = 30_000;
const INITIAL_RETRY_MS = 1_000;
// Keep in sync with the backend's WS_PRESENCE_HEARTBEAT_INTERVAL_SECONDS
// (core/config/settings.py) — no shared config channel between the two.
const HEARTBEAT_INTERVAL_MS = 25_000;

/**
 * Maintains a single WebSocket connection to the backend event stream
 * while the current user is authenticated, reconnecting with backoff on
 * drops. Incoming `message.created` events are merged into the matching
 * chat-messages cache; `presence.update` events are applied to the
 * friends/server presence caches; `typing.update` events are applied to
 * the typing store. Also sends periodic heartbeats carrying the client's
 * idle state, which the server uses to derive Away, and invalidates
 * presence queries on every reconnect (Redis pub/sub has no replay, so a
 * presence.update published during a dropped connection is otherwise
 * silently missed — typing needs no equivalent catch-up, it just clears
 * itself out via the typing store's own auto-expiry).
 */
export function RealtimeProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();
  const userId = user?.id;
  const idle = useIdle();
  const idleRef = useRef(idle);

  useEffect(() => {
    idleRef.current = idle;
  }, [idle]);

  const socketRef = useRef<WebSocket | null>(null);
  const wasIdleRef = useRef(idle);

  useEffect(() => {
    // Coming back from idle reads as responsive rather than waiting up to
    // one full heartbeat interval — going idle can wait for the next tick.
    if (wasIdleRef.current && !idle) {
      const socket = socketRef.current;
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "heartbeat", idle: false }));
      }
    }
    wasIdleRef.current = idle;
  }, [idle]);

  useEffect(() => {
    if (!userId) return;

    let retryMs = INITIAL_RETRY_MS;
    let retryTimer: number | undefined;
    let heartbeatTimer: number | undefined;
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
      } else if (isPresenceUpdateEvent(parsed)) {
        applyPresenceUpdate(queryClient, parsed.payload);
      } else if (isTypingUpdateEvent(parsed)) {
        const { chat_id, user_id, is_typing } = parsed.payload;
        useTypingStore
          .getState()
          .applyTypingUpdate(chat_id, user_id, is_typing);
      }
    };

    const connect = () => {
      const socket = new WebSocket(getWsEventsUrl());
      socketRef.current = socket;
      socket.onopen = () => {
        retryMs = INITIAL_RETRY_MS;
        setSocketSend((data) => socket.send(JSON.stringify(data)));
        void queryClient.invalidateQueries({ queryKey: ["presence"] });
        // Chat-room membership (unlike presence's user_room) is joined as
        // a side effect of GET .../messages, and only reaches this user's
        // *currently open* connections (see backend
        // ConnectionManager.join_user_to_room) — a silent no-op if that
        // request lands before this connection exists at all (a real race
        // on first page load) or after any prior connection dropped (any
        // reconnect: a network blip, a backend restart, laptop sleep).
        // Refetching here, now that this connection is guaranteed open,
        // re-joins whichever chat(s) are currently mounted — without it,
        // a dropped-and-reconnected socket would silently never receive
        // further messages or typing events for an already-open chat.
        void queryClient.invalidateQueries({ queryKey: ["chat-messages"] });
        heartbeatTimer = window.setInterval(() => {
          socket.send(
            JSON.stringify({ type: "heartbeat", idle: idleRef.current }),
          );
        }, HEARTBEAT_INTERVAL_MS);
      };
      socket.onmessage = handleEvent;
      socket.onerror = () => socket.close();
      socket.onclose = () => {
        setSocketSend(() => {});
        window.clearInterval(heartbeatTimer);
        if (socketRef.current === socket) socketRef.current = null;
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
      setSocketSend(() => {});
      window.clearTimeout(retryTimer);
      window.clearInterval(heartbeatTimer);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [userId, queryClient]);

  return <>{children}</>;
}
