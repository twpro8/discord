// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getFriendsPresence } from "../api/get-friends-presence";

/** Presence for the current user's friends — REST catch-up, kept fresh by
 * `presence.update` events applied in RealtimeProvider. */
export function useFriendsPresence() {
  return useQuery({
    queryKey: ["presence", "friends"],
    queryFn: getFriendsPresence,
  });
}
