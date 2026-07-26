/** Friend request or relationship enriched with the other user's profile. */
export interface FriendRequestWithUser {
  id: string;
  user_id: string;
  target_user_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  username: string;
  avatar_url: string | null;
}
