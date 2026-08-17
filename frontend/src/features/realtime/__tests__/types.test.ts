import {
  isCallAcceptedEvent,
  isCallAnswerEvent,
  isCallBusyEvent,
  isCallCancelledEvent,
  isCallHangupEvent,
  isCallIceCandidateEvent,
  isCallInviteEvent,
  isCallMediaStateEvent,
  isCallOfferEvent,
  isCallRejectedEvent,
  isCallTimeoutEvent,
  isErrorEvent,
  isMessageCreatedEvent,
  isPresenceUpdateEvent,
  isTypingUpdateEvent,
} from "../types";

describe("isPresenceUpdateEvent", () => {
  it("returns true for a presence.update event", () => {
    const event = {
      type: "presence.update" as const,
      payload: { user_id: "u1", status: "online" as const, last_seen_at: null },
    };
    expect(isPresenceUpdateEvent(event)).toBe(true);
    expect(isMessageCreatedEvent(event)).toBe(false);
    expect(isTypingUpdateEvent(event)).toBe(false);
  });

  it("returns false for a message.created event", () => {
    const event = {
      type: "message.created" as const,
      payload: {} as never,
    };
    expect(isPresenceUpdateEvent(event)).toBe(false);
    expect(isMessageCreatedEvent(event)).toBe(true);
    expect(isTypingUpdateEvent(event)).toBe(false);
  });
});

describe("isTypingUpdateEvent", () => {
  it("returns true for a typing.update event", () => {
    const event = {
      type: "typing.update" as const,
      payload: { chat_id: "c1", user_id: "u1", is_typing: true },
    };
    expect(isTypingUpdateEvent(event)).toBe(true);
    expect(isMessageCreatedEvent(event)).toBe(false);
    expect(isPresenceUpdateEvent(event)).toBe(false);
  });

  it("returns false for a presence.update event", () => {
    const event = {
      type: "presence.update" as const,
      payload: { user_id: "u1", status: "online" as const, last_seen_at: null },
    };
    expect(isTypingUpdateEvent(event)).toBe(false);
  });
});

describe("call event guards", () => {
  it("isCallInviteEvent narrows call.invite and rejects other call events", () => {
    const event = {
      type: "call.invite" as const,
      payload: {
        call_id: "c1",
        chat_id: "ch1",
        caller_id: "u1",
        callee_id: "u2",
      },
    };
    expect(isCallInviteEvent(event)).toBe(true);
    expect(isCallAcceptedEvent(event)).toBe(false);
  });

  it("isCallAcceptedEvent narrows call.accepted", () => {
    const event = {
      type: "call.accepted" as const,
      payload: { call_id: "c1" },
    };
    expect(isCallAcceptedEvent(event)).toBe(true);
    expect(isCallRejectedEvent(event)).toBe(false);
  });

  it("isCallRejectedEvent narrows call.rejected", () => {
    const event = {
      type: "call.rejected" as const,
      payload: { call_id: "c1" },
    };
    expect(isCallRejectedEvent(event)).toBe(true);
    expect(isCallCancelledEvent(event)).toBe(false);
  });

  it("isCallCancelledEvent narrows call.cancelled", () => {
    const event = {
      type: "call.cancelled" as const,
      payload: { call_id: "c1" },
    };
    expect(isCallCancelledEvent(event)).toBe(true);
    expect(isCallTimeoutEvent(event)).toBe(false);
  });

  it("isCallBusyEvent narrows call.busy", () => {
    const event = {
      type: "call.busy" as const,
      payload: { call_id: "c1", reason: "callee_busy" as const },
    };
    expect(isCallBusyEvent(event)).toBe(true);
    expect(isCallHangupEvent(event)).toBe(false);
  });

  it("isCallTimeoutEvent narrows call.timeout", () => {
    const event = { type: "call.timeout" as const, payload: { call_id: "c1" } };
    expect(isCallTimeoutEvent(event)).toBe(true);
    expect(isCallInviteEvent(event)).toBe(false);
  });

  it("isCallHangupEvent narrows call.hangup", () => {
    const event = {
      type: "call.hangup" as const,
      payload: { call_id: "c1", reason: "hangup" as const },
    };
    expect(isCallHangupEvent(event)).toBe(true);
    expect(isCallOfferEvent(event)).toBe(false);
  });

  it("isCallOfferEvent narrows call.offer", () => {
    const event = {
      type: "call.offer" as const,
      payload: { call_id: "c1", sdp: { type: "offer" as const, sdp: "" } },
    };
    expect(isCallOfferEvent(event)).toBe(true);
    expect(isCallAnswerEvent(event)).toBe(false);
  });

  it("isCallAnswerEvent narrows call.answer", () => {
    const event = {
      type: "call.answer" as const,
      payload: { call_id: "c1", sdp: { type: "answer" as const, sdp: "" } },
    };
    expect(isCallAnswerEvent(event)).toBe(true);
    expect(isCallIceCandidateEvent(event)).toBe(false);
  });

  it("isCallIceCandidateEvent narrows call.ice_candidate", () => {
    const event = {
      type: "call.ice_candidate" as const,
      payload: { call_id: "c1", candidate: {} },
    };
    expect(isCallIceCandidateEvent(event)).toBe(true);
    expect(isErrorEvent(event)).toBe(false);
  });

  it("isCallMediaStateEvent narrows call.media_state", () => {
    const event = {
      type: "call.media_state" as const,
      payload: { call_id: "c1", video_camera: true, video_screen: false },
    };
    expect(isCallMediaStateEvent(event)).toBe(true);
    expect(isCallOfferEvent(event)).toBe(false);
  });

  it("isErrorEvent narrows the generic error event", () => {
    const event = { type: "error" as const, payload: { code: "unauthorized" } };
    expect(isErrorEvent(event)).toBe(true);
    expect(isCallInviteEvent(event)).toBe(false);
  });
});
