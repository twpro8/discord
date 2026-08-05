// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getServerPresence } from "../api/get-server-presence";

/** Presence for every member of a server — REST catch-up, kept fresh by
 * `presence.update` events applied in RealtimeProvider. */
export function useServerPresence(serverId: string) {
  return useQuery({
    queryKey: ["presence", "server", serverId],
    queryFn: () => getServerPresence(serverId),
  });
}
