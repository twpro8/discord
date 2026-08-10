import { act, renderHook } from "@testing-library/react";
import type { Mock } from "vitest";

import { setSocketSend } from "@/features/realtime/model/socket-sender";

import { useSendTyping } from "../use-send-typing";

describe("useSendTyping", () => {
  let send: Mock<(data: unknown) => void>;

  beforeEach(() => {
    vi.useFakeTimers();
    send = vi.fn<(data: unknown) => void>();
    setSocketSend(send);
  });

  afterEach(() => {
    setSocketSend(() => {});
    vi.useRealTimers();
  });

  it("sends a typing:true frame on the first call", () => {
    const { result } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyTyping();
    });

    expect(send).toHaveBeenCalledTimes(1);
    expect(send).toHaveBeenCalledWith({
      type: "typing",
      chat_id: "chat-1",
      is_typing: true,
    });
  });

  it("does not resend within the throttle window", () => {
    const { result } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyTyping();
      vi.advanceTimersByTime(1_000);
      result.current.notifyTyping();
    });

    expect(send).toHaveBeenCalledTimes(1);
  });

  it("resends once the throttle window has elapsed", () => {
    const { result } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyTyping();
      vi.advanceTimersByTime(3_000);
      result.current.notifyTyping();
    });

    expect(send).toHaveBeenCalledTimes(2);
  });

  it("sends an immediate stop only if typing was previously sent", () => {
    const { result } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyTyping();
      result.current.notifyStopTyping();
    });

    expect(send).toHaveBeenCalledTimes(2);
    expect(send).toHaveBeenLastCalledWith({
      type: "typing",
      chat_id: "chat-1",
      is_typing: false,
    });
  });

  it("does not send a stop if typing was never started", () => {
    const { result } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyStopTyping();
    });

    expect(send).not.toHaveBeenCalled();
  });

  it("sends a stop on unmount", () => {
    const { result, unmount } = renderHook(() => useSendTyping("chat-1"));

    act(() => {
      result.current.notifyTyping();
    });
    send.mockClear();

    unmount();

    expect(send).toHaveBeenCalledWith({
      type: "typing",
      chat_id: "chat-1",
      is_typing: false,
    });
  });
});
