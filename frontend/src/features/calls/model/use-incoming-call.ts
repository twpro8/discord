// react
import { useEffect, useRef, useState } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import {
  getUserChannel,
  subscribeToCallCancelled,
  subscribeToIncomingCalls,
} from "@/shared/api/socket";

// relative
import { getUserById } from "../api/get-user";

/** Tracks an incoming call broadcast on the current user's Phoenix
 * `user:{id}` channel. Joins the channel (idempotently) and subscribes
 * to `incoming_call` and `call_cancelled` exactly once per user,
 * surfacing the caller's id to the UI through `callerId`. `dismiss` is
 * only for a deliberate decline by this user — being cancelled by the
 * caller closes the window (with an informative toast) without pushing
 * `decline_call` back. */
export function useIncomingCall(userId?: string) {
  const [callerId, setCallerId] = useState<string | null>(null);
  const callerIdRef = useRef<string | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    callerIdRef.current = callerId;
  }, [callerId]);

  function dismiss() {
    setCallerId(null);

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

  useEffect(() => {
    if (!userId) return;

    getUserChannel(userId);

    subscribeToIncomingCalls((payload) => {
      setCallerId((payload as { caller_id: string }).caller_id);
    });

    subscribeToCallCancelled(async (payload) => {
      const caller = (payload as { caller_id: string }).caller_id;
      if (callerIdRef.current !== caller) return;

      setCallerId(null);

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
  }, [queryClient, userId]);

  return { callerId, dismiss };
}
