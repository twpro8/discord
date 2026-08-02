// relative
import type { FriendRequestWithUser } from "./types";

/** Resolves the other user's id for an accepted friend relationship. */
export function getFriendPeerId(
  friend: FriendRequestWithUser,
  currentUserId: string,
): string {
  if (friend.user_id === currentUserId) {
    return friend.target_user_id;
  }
  return friend.user_id;
}
