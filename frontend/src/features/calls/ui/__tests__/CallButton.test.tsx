import { render, screen } from "@testing-library/react";
import { toast } from "sonner";
import { vi } from "vitest";

import { useCallStore } from "../../model/use-call-store";
import { CallButton } from "../CallButton";

const startCallMock = vi.fn();

vi.mock("../../model/use-start-call", () => ({
  useStartCall: () => ({ startCall: startCallMock }),
}));
vi.mock("sonner", () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

describe("CallButton", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
    startCallMock.mockClear();
    vi.mocked(toast.error).mockClear();
    // jsdom has no WebRTC implementation at all — stub the two feature
    // checks CallButton looks at so "supported" tests reflect a real
    // browser instead of always hitting the unsupported path.
    vi.stubGlobal("RTCPeerConnection", vi.fn());
    Object.defineProperty(navigator, "mediaDevices", {
      value: { getUserMedia: vi.fn() },
      configurable: true,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("is enabled when idle, a peer is known, and WebRTC is supported", () => {
    render(<CallButton chatId="chat-1" peerId="peer-1" peerName="Bob" />);

    expect(
      screen.getByRole("button", { name: "Start voice call" }),
    ).toBeEnabled();
  });

  it("is disabled while already in a call", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: { getTracks: () => [] } as unknown as MediaStream,
    });

    render(<CallButton chatId="chat-1" peerId="peer-1" peerName="Bob" />);

    expect(
      screen.getByRole("button", { name: "Start voice call" }),
    ).toBeDisabled();
  });

  it("stays enabled while the peer hasn't resolved yet", () => {
    // A direct/bookmarked navigation to a DM URL can leave peerId
    // unresolved for a moment (see DmChatView's chatDetails-vs-search-
    // param comment); the button must not flicker disabled for a purely
    // timing-dependent reason.
    render(<CallButton chatId="chat-1" peerName="Bob" />);

    expect(
      screen.getByRole("button", { name: "Start voice call" }),
    ).toBeEnabled();
  });

  it("shows a toast instead of starting a call when clicked before the peer resolves", () => {
    render(<CallButton chatId="chat-1" peerName="Bob" />);

    screen.getByRole("button", { name: "Start voice call" }).click();

    expect(startCallMock).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalledWith(
      "Still loading this chat — try calling again in a moment.",
    );
  });

  it("is disabled when the browser has no RTCPeerConnection support", () => {
    vi.stubGlobal("RTCPeerConnection", undefined);

    render(<CallButton chatId="chat-1" peerId="peer-1" peerName="Bob" />);

    expect(
      screen.getByRole("button", { name: "Start voice call" }),
    ).toBeDisabled();
  });

  it("starts a call on click when enabled", async () => {
    render(<CallButton chatId="chat-1" peerId="peer-1" peerName="Bob" />);

    screen.getByRole("button", { name: "Start voice call" }).click();

    expect(startCallMock).toHaveBeenCalledWith("chat-1", "peer-1", "Bob");
  });
});
