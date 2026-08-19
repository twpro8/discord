// react
import { useEffect } from "react";

// third party
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getUserChannel, subscribeToDeclinedCall } from "@/shared/api/socket";

// relative
import { getUserById } from "../api/get-user";
import { useOutgoingCall } from "./use-outgoing-call";

/** Listens for `declined_call` broadcasts — the callee rejecting the
 * current user's outgoing call — closing the outgoing-call window and
 * surfacing an informative toast. Matching against the store's `peerId`
 * keeps an unrelated decline from closing a different call. The callee's
 * name comes from the shared `["user", id]` query cache, so no extra
 * request fires when the peer was already shown in the call window. */
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
  }, [queryClient, userId]);
}
