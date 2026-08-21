// react
import { useEffect } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import {
  getUserChannel,
  subscribeToCallAccepted,
  subscribeToDeclinedCall,
} from "@/shared/api/socket";

// relative
import { getUserById } from "../api/get-user";
import { useOutgoingCall } from "./use-outgoing-call";

/** Listens for `declined_call` and `call_accepted` broadcasts on the
 * current user's Phoenix channel. On decline, shows a toast and clears
 * the outgoing-call state. On accept, stores the accepted callId so
 * WebRTC can begin. Matching against the store's `callId` keeps
 * unrelated events from affecting a different call. */
export function useOutgoingCallEvents(userId?: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!userId) return;

    getUserChannel(userId);

    subscribeToDeclinedCall(async (payload) => {
      const declinedBy = (payload as { target_user_id: string }).target_user_id;
      const { peerId, clear } = useOutgoingCall.getState();
      if (!peerId || peerId !== declinedBy) return;

      try {
        const user = await queryClient.ensureQueryData({
          queryKey: ["user", declinedBy],
          queryFn: () => getUserById(declinedBy),
        });
        toast.info(`${user.name ?? user.username} declined your call`);
      } catch {
        toast.info("Your call was declined");
      } finally {
        clear();
      }
    });

    subscribeToCallAccepted((payload) => {
      const { call_id } = payload as {
        call_id: string;
        callee_id: string;
      };
      const { callId, setAccepted } = useOutgoingCall.getState();
      if (callId === call_id) {
        setAccepted(call_id);
      }
    });
  }, [queryClient, userId]);
}
