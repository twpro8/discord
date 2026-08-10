// third party
import type { QueryClient } from "@tanstack/react-query";

// relative
import type { PresenceEntry } from "./types";

type PresenceUpdatePayload = PresenceEntry;

function upsertPresence(
  entries: PresenceEntry[] | undefined,
  update: PresenceUpdatePayload,
): PresenceEntry[] | undefined {
  if (!entries) return entries;
  const index = entries.findIndex((entry) => entry.user_id === update.user_id);
  if (index === -1) return entries;

  const next = [...entries];
  next[index] = update;
  return next;
}

/**
 * Applies an incoming `presence.update` event to every cache that might
 * hold that user — the friends-presence cache and any open server-presence
 * cache(s). Only updates entries that already exist in a given cache
 * (learning about a *new* friend/member happens via that list's own query,
 * not through a presence event).
 */
export function applyPresenceUpdate(
  queryClient: QueryClient,
  update: PresenceUpdatePayload,
) {
  queryClient.setQueryData<PresenceEntry[]>(["presence", "friends"], (prev) =>
    upsertPresence(prev, update),
  );
  queryClient.setQueriesData<PresenceEntry[]>(
    { queryKey: ["presence", "server"] },
    (prev) => upsertPresence(prev, update),
  );
}
