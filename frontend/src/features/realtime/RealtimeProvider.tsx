// react
import { useEffect, useRef, type ReactNode } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";

// shared
import { WS_EVENTS_URL } from "@/shared/config/env";

// features
import {
  handleCallAccepted,
  handleCallAnswer,
  handleCallBusy,
  handleCallCancelled,
  handleCallError,
  handleCallHangup,
  handleCallIceCandidate,
  handleCallInvite,
  handleCallOffer,
  handleCallRejected,
  handleCallTimeout,
} from "@/features/calls/model/use-call-signal-handlers";
import { useCallStore } from "@/features/calls/model/use-call-store";
import { teardown as teardownCall } from "@/features/calls/model/webrtc-session";
import { mergeIncomingMessages } from "@/features/chats/model/use-chat-messages";
import { applyPresenceUpdate } from "@/features/presence/model/apply-presence-update";
import { useCurrentUser } from "@/features/profile/model/use-current-user";
import { useTypingStore } from "@/features/typing/model/use-typing-store";

// relative
import { setSocketSend } from "./model/socket-sender";
import { useIdle } from "./model/use-idle";
import {
  isCallAcceptedEvent,
  isCallAnswerEvent,
  isCallBusyEvent,
  isCallCancelledEvent,
  isCallHangupEvent,
  isCallIceCandidateEvent,
  isCallInviteEvent,
  isCallOfferEvent,
  isCallRejectedEvent,
  isCallTimeoutEvent,
  isErrorEvent,
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
 * the typing store; `call.*`/`error` events are routed into the call
 * store + WebRTC session via use-call-signal-handlers.ts. Also sends
 * periodic heartbeats carrying the client's idle state, which the server
 * uses to derive Away, and invalidates presence queries on every
 * reconnect (Redis pub/sub has no replay, so a presence.update published
 * during a dropped connection is otherwise silently missed — typing
 * needs no equivalent catch-up, it just clears itself out via the typing
 * store's own auto-expiry; an in-progress call instead treats the drop
 * itself as the call ending, see the `onclose` handler below).
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
      } else if (isCallInviteEvent(parsed)) {
        if (userId) handleCallInvite(parsed.payload, userId);
      } else if (isCallAcceptedEvent(parsed)) {
        handleCallAccepted(parsed.payload);
      } else if (isCallRejectedEvent(parsed)) {
        handleCallRejected(parsed.payload);
      } else if (isCallCancelledEvent(parsed)) {
        handleCallCancelled(parsed.payload);
      } else if (isCallBusyEvent(parsed)) {
        handleCallBusy(parsed.payload);
      } else if (isCallTimeoutEvent(parsed)) {
        handleCallTimeout(parsed.payload);
      } else if (isCallHangupEvent(parsed)) {
        handleCallHangup(parsed.payload);
      } else if (isCallOfferEvent(parsed)) {
        handleCallOffer(parsed.payload);
      } else if (isCallAnswerEvent(parsed)) {
        handleCallAnswer(parsed.payload);
      } else if (isCallIceCandidateEvent(parsed)) {
        handleCallIceCandidate(parsed.payload);
      } else if (isErrorEvent(parsed)) {
        handleCallError(parsed.payload);
      }
    };

    const connect = () => {
      const socket = new WebSocket(WS_EVENTS_URL);
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
        // A dropped socket mid-call is treated as a dropped call — no
        // resume-signaling semantics make sense for a live media session
        // (see plan §6, "Network blip"). Applies on every close, not just
        // a genuine disposal, since a reconnect-in-progress still means
        // the call's signaling channel was gone for a period.
        if (useCallStore.getState().phase !== "idle") {
          teardownCall();
          useCallStore.getState().endCall("disconnected");
        }
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
