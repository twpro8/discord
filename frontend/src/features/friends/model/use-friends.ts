// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getFriends } from "../api/get-friends";

/** Returns the current user's friend list. */
export function useFriends() {
  return useQuery({
    queryKey: ["friends"],
    queryFn: getFriends,
    retry: false,
  });
}
