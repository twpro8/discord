// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getCurrentUser } from "../api/get-me";

/** Returns the currently authenticated user. */
export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
}
