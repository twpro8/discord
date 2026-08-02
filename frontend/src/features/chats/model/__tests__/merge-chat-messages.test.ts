import { mergeChatMessages } from "../merge-chat-messages";
import type { ChatMessage } from "../types";

function makeMessage(
  id: string,
  createdAt: string,
  overrides: Partial<ChatMessage> = {},
): ChatMessage {
  return {
    id,
    sender_id: "user-a",
    body: `message ${id}`,
    sequence: 1,
    parent_id: null,
    is_edited: false,
    is_deleted: false,
    deleted_at: null,
    created_at: createdAt,
    updated_at: createdAt,
    chat_id: "chat-1",
    ...overrides,
  };
}

describe("mergeChatMessages", () => {
  it("returns existing messages when incoming is empty", () => {
    const existing = [makeMessage("1", "2026-08-02T10:00:00Z")];
    expect(mergeChatMessages(existing, [])).toEqual(existing);
  });

  it("appends incoming messages in chronological order", () => {
    const existing = [makeMessage("1", "2026-08-02T10:00:00Z")];
    const incoming = [makeMessage("2", "2026-08-02T10:05:00Z")];

    expect(mergeChatMessages(existing, incoming).map((m) => m.id)).toEqual([
      "1",
      "2",
    ]);
  });

  it("deduplicates by id, preferring the incoming copy", () => {
    const existing = [
      makeMessage("1", "2026-08-02T10:00:00Z", { body: "stale" }),
    ];
    const incoming = [
      makeMessage("1", "2026-08-02T10:00:00Z", { body: "fresh" }),
    ];

    const merged = mergeChatMessages(existing, incoming);
    expect(merged).toHaveLength(1);
    expect(merged[0].body).toBe("fresh");
  });

  it("sorts combined messages by created_at", () => {
    const existing = [makeMessage("3", "2026-08-02T10:10:00Z")];
    const incoming = [
      makeMessage("2", "2026-08-02T10:05:00Z"),
      makeMessage("1", "2026-08-02T10:00:00Z"),
    ];

    expect(mergeChatMessages(existing, incoming).map((m) => m.id)).toEqual([
      "1",
      "2",
      "3",
    ]);
  });
});
