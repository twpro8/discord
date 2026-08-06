// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import {
  updateProfile,
  type UpdateProfilePayload,
} from "../api/update-profile";

/** Updates the current user's profile fields and refreshes the cached user. */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["current-user"] });
      toast.success("Profile updated");
    },
    onError: (error) => {
      toast.error(getApiError(error));
    },
  });
}

export type { UpdateProfilePayload };
