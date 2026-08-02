// third party
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { createPrivateChat } from "../api/create-chat";

/**
 * Creates (or returns the existing) private chat with a peer. Callers
 * navigate to the returned chat's route on success.
 */
export function useCreatePrivateChat() {
  return useMutation({
    mutationFn: createPrivateChat,
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
