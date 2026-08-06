// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { updateAvatar } from "../api/update-avatar";

/** Uploads a new avatar and refreshes the cached user. */
export function useUpdateAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateAvatar,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["current-user"] });
      toast.success("Avatar updated");
    },
    onError: (error) => {
      toast.error(getApiError(error));
    },
  });
}
