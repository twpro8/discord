/** A server member enriched with the user's profile — the roster shown on
 * the server members page. */
export interface ServerMemberWithUser {
  id: string;
  user_id: string;
  username: string;
  avatar_url: string | null;
  role: string;
}
