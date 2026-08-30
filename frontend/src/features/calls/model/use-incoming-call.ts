// react
import { useEffect, useRef, useState } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import {
  getUserChannel,
  subscribeToCallAccepted,
  subscribeToCallCancelled,
  subscribeToIncomingCalls,
} from "@/shared/api/socket";

// relative
import { getUserById } from "../api/get-user";

/** Tracks an incoming call broadcast on the current user's Phoenix
 * `user:{id}` channel. Unified room: `room_id` (alias `call_id`) for 1:1, group
 * and server voice. Joins the channel (idempotently) and subscribes to
 * `incoming_call`, `call_cancelled`, and `call_accepted` exactly once per user,
 * surfacing the caller's id to the UI through `callerId`. When the callee accepts,
 * `acceptedCallId` (alias `acceptedRoomId`) is set so WebRTC can start. */
export function useIncomingCall(userId?: string) {
  const [callerId, setCallerId] = useState<string | null>(null);
  const [callId, setCallId] = useState<string | null>(null);
  const [acceptedCallId, setAcceptedCallId] = useState<string | null>(null);
  const callerIdRef = useRef<string | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    callerIdRef.current = callerId;
  }, [callerId]);

  function dismiss() {
    setCallerId(null);
    setCallId(null);
    setAcceptedCallId(null);

    if (!userId) return;

    getUserChannel(userId)
      .push("decline_call", { caller_id: callerId })
      .receive("ok", () => {
        console.log("Call is declined");
      })
      .receive("error", (error: unknown) => {
        console.error("Call decline failed:", error);
      });
  }

  function acceptCall() {
    if (!userId || !callId || !callerId) return;

    setAcceptedCallId(callId);

    getUserChannel(userId)
      .push("accept_call", {
        caller_id: callerId,
        call_id: callId,
        room_id: callId,
      })
      .receive("ok", () => {
        console.log("Call accepted");
      })
      .receive("error", (error: unknown) => {
        console.error("Call accept failed:", error);
      });
  }

  useEffect(() => {
    if (!userId) return;

    getUserChannel(userId);

    subscribeToIncomingCalls((payload) => {
      const data = payload as {
        caller_id: string;
        call_id?: string;
        room_id?: string;
        participant_ids?: string[];
      };
      const roomId = data.room_id ?? data.call_id;
      if (!roomId) return;
      setCallerId(data.caller_id);
      setCallId(roomId);
      setAcceptedCallId(null);
    });

    subscribeToCallCancelled(async (payload) => {
      const caller = (payload as { caller_id: string }).caller_id;
      if (callerIdRef.current !== caller) return;

      setCallerId(null);
      setCallId(null);
      setAcceptedCallId(null);

      try {
        const canceller = await queryClient.ensureQueryData({
          queryKey: ["user", caller],
          queryFn: () => getUserById(caller),
        });
        toast.info(
          `${canceller.name ?? canceller.username} cancelled the call`,
        );
      } catch {
        toast.info("The call was cancelled");
      }
    });

    subscribeToCallAccepted((payload) => {
      const data = payload as {
        call_id?: string;
        room_id?: string;
        callee_id: string;
      };
      if (data.callee_id !== userId) return;
      const roomId = data.room_id ?? data.call_id;
      if (!roomId) return;
      setAcceptedCallId(roomId);
      setCallerId(null);
      setCallId(null);
    });
  }, [queryClient, userId]);

  return {
    callerId,
    callId,
    /** Alias for unified room: roomId == callId */
    roomId: callId,
    acceptedCallId,
    acceptedRoomId: acceptedCallId,
    acceptCall,
    dismiss,
  };
}
