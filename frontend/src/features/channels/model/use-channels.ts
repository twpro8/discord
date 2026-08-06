// third party
import { useQuery, useQueryClient } from "@tanstack/react-query";

// relative
import { getServerChannels } from "../api/get-channels";

/** Returns a server's channels with an invalidate helper. The list
 * endpoint doesn't exist in the backend yet, so failures surface as an
 * empty list rather than an error toast — the sidebar shows an empty
 * state until channels can be fetched. */
export function useChannels(serverId: string) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["channels", serverId],
    queryFn: () => getServerChannels(serverId),
    retry: false,
  });

  return {
    ...query,
    data: query.isError ? [] : query.data,
    invalidate: () =>
      queryClient.invalidateQueries({ queryKey: ["channels", serverId] }),
  };
}
