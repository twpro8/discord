import { isMessageCreatedEvent, isPresenceUpdateEvent } from "../types";

describe("isPresenceUpdateEvent", () => {
  it("returns true for a presence.update event", () => {
    const event = {
      type: "presence.update" as const,
      payload: { user_id: "u1", status: "online" as const, last_seen_at: null },
    };
    expect(isPresenceUpdateEvent(event)).toBe(true);
    expect(isMessageCreatedEvent(event)).toBe(false);
  });

  it("returns false for a message.created event", () => {
    const event = {
      type: "message.created" as const,
      payload: {} as never,
    };
    expect(isPresenceUpdateEvent(event)).toBe(false);
    expect(isMessageCreatedEvent(event)).toBe(true);
  });
});
