// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { createChannel, type CreateChannelInput } from "../api/create-channel";

/** Creates a channel in a server, refreshing the channels list on success. */
export function useCreateChannel(serverId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreateChannelInput) => createChannel(serverId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["channels", serverId] });
      toast.success("Channel created successfully");
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
