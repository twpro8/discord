// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// entities
import type { User } from "@/entities/user/model/types";

// relative
import { updateAvatar } from "../api/update-avatar";

/** Uploads a new avatar and replaces the cached user so every consumer of
 * `useCurrentUser` re-renders with the fresh avatar immediately. */
export function useUpdateAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateAvatar,
    onSuccess: (data: User) => {
      queryClient.setQueryData(["current-user"], data);
      toast.success("Avatar updated");
    },
    onError: (error) => {
      toast.error(getApiError(error));
    },
  });
}
