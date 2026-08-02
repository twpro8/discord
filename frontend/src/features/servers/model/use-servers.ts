// react
import { useEffect } from "react";

// third party
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { getMyServers } from "../api/get-servers";

/** Returns the current user's servers with an invalidate helper. */
export function useServers() {
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();

  const query = useQuery({
    queryKey: ["servers", user?.id],
    queryFn: getMyServers,
    enabled: Boolean(user?.id),
    retry: false,
  });

  useEffect(() => {
    if (query.isError) {
      const message =
        query.error instanceof Error
          ? query.error.message
          : "Unable to load servers";
      toast.error(message);
    }
  }, [query.error, query.isError]);

  return {
    ...query,
    invalidate: () =>
      queryClient.invalidateQueries({ queryKey: ["servers", user?.id] }),
  };
}
