// third party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { acceptFriendRequest } from "../api/accept-friend-request";
import { deleteFriendRequest } from "../api/delete-friend-request";
import { removeFriend } from "../api/remove-friend";

/** Mutation to accept an incoming friend request. */
export function useAcceptFriendRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: acceptFriendRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["friend-requests"] });
      queryClient.invalidateQueries({ queryKey: ["friends"] });
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}

/** Mutation to cancel or decline a friend request. */
export function useDeleteFriendRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteFriendRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["friend-requests"] });
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}

/** Mutation to remove a friend from the friend list. */
export function useRemoveFriend() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeFriend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["friends"] });
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
