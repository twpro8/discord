// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { sendChatMessage } from "../api/send-chat-message";
import { appendChatMessage } from "./use-chat-messages";

/** Sends a message to a chat and appends the persisted copy to the cache. */
export function useSendChatMessage(chatId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: string) => sendChatMessage(chatId, body),
    onSuccess: (message) => {
      appendChatMessage(queryClient, chatId, message);
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
