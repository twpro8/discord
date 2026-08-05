// shared
import { api } from "@/shared/api/axios";

// relative
import type { PresenceEntry } from "../model/types";

/** Fetches the current user's friends' presence — the REST catch-up path
 * for when a `presence.update` event was missed (e.g. during a dropped
 * WebSocket reconnect). */
export async function getFriendsPresence(): Promise<PresenceEntry[]> {
  const response = await api.get<PresenceEntry[]>("/presence/friends");
  return response.data;
}
