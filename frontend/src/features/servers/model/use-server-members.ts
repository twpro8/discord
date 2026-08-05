// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getServerMembers } from "../api/get-server-members";

/** Returns a server's member roster. */
export function useServerMembers(serverId: string) {
  return useQuery({
    queryKey: ["server-members", serverId],
    queryFn: () => getServerMembers(serverId),
  });
}
