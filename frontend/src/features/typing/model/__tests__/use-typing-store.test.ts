import { useTypingStore } from "../use-typing-store";

const AUTO_EXPIRE_MS = 7_000;

describe("useTypingStore", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useTypingStore.setState({ typingByChat: {} });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sets a user as typing in a chat", () => {
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);

    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({
      "user-1": true,
    });
  });

  it("clears a user immediately on an explicit false update", () => {
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", false);

    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({});
  });

  it("auto-expires a typing entry after the timeout with no renewal", () => {
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);

    vi.advanceTimersByTime(AUTO_EXPIRE_MS + 1);

    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({});
  });

  it("resets the auto-expiry timer on a renewed true update", () => {
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);

    vi.advanceTimersByTime(AUTO_EXPIRE_MS - 1_000);
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);
    vi.advanceTimersByTime(2_000);

    // Still typing: the original timer would have fired by now, but the
    // renewal pushed expiry out further.
    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({
      "user-1": true,
    });

    vi.advanceTimersByTime(AUTO_EXPIRE_MS);

    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({});
  });

  it("keeps different chats and users independent", () => {
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", true);
    useTypingStore.getState().applyTypingUpdate("chat-1", "user-2", true);
    useTypingStore.getState().applyTypingUpdate("chat-2", "user-1", true);

    useTypingStore.getState().applyTypingUpdate("chat-1", "user-1", false);

    expect(useTypingStore.getState().typingByChat["chat-1"]).toEqual({
      "user-2": true,
    });
    expect(useTypingStore.getState().typingByChat["chat-2"]).toEqual({
      "user-1": true,
    });
  });
});
