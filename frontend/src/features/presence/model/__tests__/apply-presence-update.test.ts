import { QueryClient } from "@tanstack/react-query";

import { applyPresenceUpdate } from "../apply-presence-update";
import type { PresenceEntry } from "../types";

function makeEntry(overrides: Partial<PresenceEntry> = {}): PresenceEntry {
  return {
    user_id: "u1",
    status: "online",
    last_seen_at: null,
    ...overrides,
  };
}

describe("applyPresenceUpdate", () => {
  it("updates an existing entry in the friends cache", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<PresenceEntry[]>(
      ["presence", "friends"],
      [makeEntry({ user_id: "u1", status: "online" })],
    );

    applyPresenceUpdate(
      queryClient,
      makeEntry({ user_id: "u1", status: "away" }),
    );

    expect(
      queryClient.getQueryData<PresenceEntry[]>(["presence", "friends"]),
    ).toEqual([makeEntry({ user_id: "u1", status: "away" })]);
  });

  it("leaves an unrelated cache entry untouched", () => {
    const queryClient = new QueryClient();
    const other = makeEntry({ user_id: "u2", status: "offline" });
    queryClient.setQueryData<PresenceEntry[]>(
      ["presence", "friends"],
      [makeEntry({ user_id: "u1", status: "online" }), other],
    );

    applyPresenceUpdate(
      queryClient,
      makeEntry({ user_id: "u1", status: "offline" }),
    );

    const updated = queryClient.getQueryData<PresenceEntry[]>([
      "presence",
      "friends",
    ]);
    expect(updated).toContainEqual(other);
  });

  it("does not insert an entry for a user not already in the cache", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<PresenceEntry[]>(["presence", "friends"], []);

    applyPresenceUpdate(queryClient, makeEntry({ user_id: "unknown" }));

    expect(
      queryClient.getQueryData<PresenceEntry[]>(["presence", "friends"]),
    ).toEqual([]);
  });

  it("does nothing when the friends cache has never been fetched", () => {
    const queryClient = new QueryClient();

    applyPresenceUpdate(queryClient, makeEntry());

    expect(
      queryClient.getQueryData<PresenceEntry[]>(["presence", "friends"]),
    ).toBeUndefined();
  });

  it("updates every open server-presence cache that has the entry", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<PresenceEntry[]>(
      ["presence", "server", "server-1"],
      [makeEntry({ user_id: "u1", status: "online" })],
    );
    queryClient.setQueryData<PresenceEntry[]>(
      ["presence", "server", "server-2"],
      [makeEntry({ user_id: "u1", status: "online" })],
    );

    applyPresenceUpdate(
      queryClient,
      makeEntry({ user_id: "u1", status: "away" }),
    );

    expect(
      queryClient.getQueryData<PresenceEntry[]>([
        "presence",
        "server",
        "server-1",
      ]),
    ).toEqual([makeEntry({ user_id: "u1", status: "away" })]);
    expect(
      queryClient.getQueryData<PresenceEntry[]>([
        "presence",
        "server",
        "server-2",
      ]),
    ).toEqual([makeEntry({ user_id: "u1", status: "away" })]);
  });
});
