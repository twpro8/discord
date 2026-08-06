// third party
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import {
  changePassword,
  type ChangePasswordPayload,
} from "../api/change-password";

/** Changes the current user's password. */
export function useChangePassword() {
  return useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      toast.success("Password changed");
    },
    onError: (error) => {
      toast.error(getApiError(error));
    },
  });
}

export type { ChangePasswordPayload };
