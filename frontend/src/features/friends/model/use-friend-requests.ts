// third party
import { useQuery, useQueryClient } from "@tanstack/react-query";

// relative
import { getFriendRequests } from "../api/get-friend-requests";
import { getSentRequests } from "../api/get-sent-requests";

/** Returns incoming and sent friend requests with an invalidate helper. */
export function useFriendRequests() {
  const queryClient = useQueryClient();

  const incoming = useQuery({
    queryKey: ["friend-requests", "incoming"],
    queryFn: getFriendRequests,
    retry: false,
  });

  const sent = useQuery({
    queryKey: ["friend-requests", "sent"],
    queryFn: getSentRequests,
    retry: false,
  });

  return {
    incoming: incoming.data ?? [],
    sent: sent.data ?? [],
    isLoading: incoming.isLoading || sent.isLoading,
    invalidate: () =>
      queryClient.invalidateQueries({ queryKey: ["friend-requests"] }),
  };
}
