// relative
import { Avatar, type AvatarStatus } from "./avatar";

/** Legacy alias for `Avatar` without an image source — kept so existing
 * imports and tests keep working. Prefer `Avatar` in new code. */
export type PresenceStatus = AvatarStatus;

export function AvatarInitial({
  username,
  status,
}: {
  username: string;
  status?: PresenceStatus;
}) {
  return <Avatar name={username} status={status} />;
}
