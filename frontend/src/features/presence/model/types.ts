// shared
import type { PresenceStatus } from "@/shared/ui/avatar-initial";

export type { PresenceStatus };

/** A single user's current presence, as returned by the REST catch-up
 * endpoints and carried in `presence.update` realtime events. */
export interface PresenceEntry {
  user_id: string;
  status: PresenceStatus;
  last_seen_at: string | null;
}
