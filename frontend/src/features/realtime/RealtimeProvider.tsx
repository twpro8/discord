// react
import { useEffect, useRef, type ReactNode } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";

// shared
import { WS_EVENTS_URL } from "@/shared/config/env";

// features
import { mergeIncomingMessages } from "@/features/chats/model/use-chat-messages";
import { applyPresenceUpdate } from "@/features/presence/model/apply-presence-update";
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { useIdle } from "./model/use-idle";
import {
  isMessageCreatedEvent,
  isPresenceUpdateEvent,
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
 * friends/server presence caches. Also sends periodic heartbeats carrying
 * the client's idle state, which the server uses to derive Away, and
 * invalidates presence queries on every reconnect (Redis pub/sub has no
 * replay, so a presence.update published during a dropped connection is
 * otherwise silently missed).
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
      }
    };

    const connect = () => {
      const socket = new WebSocket(WS_EVENTS_URL);
      socketRef.current = socket;
      socket.onopen = () => {
        retryMs = INITIAL_RETRY_MS;
        void queryClient.invalidateQueries({ queryKey: ["presence"] });
        heartbeatTimer = window.setInterval(() => {
          socket.send(
            JSON.stringify({ type: "heartbeat", idle: idleRef.current }),
          );
        }, HEARTBEAT_INTERVAL_MS);
      };
      socket.onmessage = handleEvent;
      socket.onerror = () => socket.close();
      socket.onclose = () => {
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
      window.clearTimeout(retryTimer);
      window.clearInterval(heartbeatTimer);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [userId, queryClient]);

  return <>{children}</>;
}
