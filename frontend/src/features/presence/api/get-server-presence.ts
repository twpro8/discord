// shared
import { api } from "@/shared/api/axios";

// relative
import type { PresenceEntry } from "../model/types";

/** Fetches presence for every member of a server — the REST catch-up path,
 * mirroring get-friends-presence.ts for the server-room fan-out. */
export async function getServerPresence(
  serverId: string,
): Promise<PresenceEntry[]> {
  const response = await api.get<PresenceEntry[]>(
    `/presence/servers/${serverId}`,
  );
  return response.data;
}
