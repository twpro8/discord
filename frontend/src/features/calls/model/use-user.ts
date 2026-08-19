// third party
import { useQuery } from "@tanstack/react-query";

// relative
import { getUserById } from "../api/get-user";

/** Returns a user's profile by id; disabled while `userId` is null. */
export function useUser(userId: string | null) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: () => getUserById(userId!),
    enabled: Boolean(userId),
  });
}
