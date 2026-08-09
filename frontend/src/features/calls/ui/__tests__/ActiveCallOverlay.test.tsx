import type { ReactNode } from "react";

import { createTestQueryClient } from "@/testing/render-hook";
import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { getFriendsPresence } from "@/features/presence/api/get-friends-presence";
import { socketSend } from "@/features/realtime/model/socket-sender";

import { useCallStore } from "../../model/use-call-store";
import { ActiveCallOverlay } from "../ActiveCallOverlay";

vi.mock("@/features/realtime/model/socket-sender", () => ({
  socketSend: vi.fn(),
}));
vi.mock("../../model/webrtc-session", () => ({
  setMuted: vi.fn(),
  teardown: vi.fn(),
}));
vi.mock("@/features/presence/api/get-friends-presence", () => ({
  getFriendsPresence: vi.fn(),
}));

const socketSendMock = vi.mocked(socketSend);
const getFriendsPresenceMock = vi.mocked(getFriendsPresence);

function renderWithQuery(ui: ReactNode) {
  const queryClient = createTestQueryClient();
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  }
  return render(ui, { wrapper: Wrapper });
}

function fakeStream(): MediaStream {
  return { getTracks: () => [] } as unknown as MediaStream;
}

describe("ActiveCallOverlay", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
    socketSendMock.mockClear();
    getFriendsPresenceMock.mockReset();
    getFriendsPresenceMock.mockResolvedValue([]);
  });

  it("renders nothing when idle", () => {
    const { container } = renderWithQuery(<ActiveCallOverlay />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing during incoming_ringing (that's IncomingCallModal's job)", () => {
    useCallStore.getState().beginIncomingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
    });

    const { container } = renderWithQuery(<ActiveCallOverlay />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows Waiting… while outgoing_ringing and the peer is offline", async () => {
    getFriendsPresenceMock.mockResolvedValue([
      { user_id: "peer-1", status: "offline", last_seen_at: null },
    ]);
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });

    renderWithQuery(<ActiveCallOverlay />);

    expect(await screen.findByText("Waiting…")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("shows Ringing… while outgoing_ringing and the peer is online", async () => {
    getFriendsPresenceMock.mockResolvedValue([
      { user_id: "peer-1", status: "online", last_seen_at: null },
    ]);
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });

    renderWithQuery(<ActiveCallOverlay />);

    expect(await screen.findByText("Ringing…")).toBeInTheDocument();
  });

  it("defaults to Ringing… while outgoing_ringing when the peer's presence is unknown", () => {
    // e.g. calling a chat peer who isn't a friend — presence.friends
    // never includes them, so this must not be misread as "offline".
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });

    renderWithQuery(<ActiveCallOverlay />);

    expect(screen.getByText("Ringing…")).toBeInTheDocument();
  });

  it("shows Connecting… while connecting", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToConnecting();

    renderWithQuery(<ActiveCallOverlay />);

    expect(screen.getByText("Connecting…")).toBeInTheDocument();
  });

  it("shows Connected while active", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    renderWithQuery(<ActiveCallOverlay />);

    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("shows Call ended (or Call failed) and hides the mute/hangup buttons once ended", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().endCall("connection_failed");

    renderWithQuery(<ActiveCallOverlay />);

    expect(screen.getByText("Call failed")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Hang up" }),
    ).not.toBeInTheDocument();
  });

  it("sends call.hangup and tears down the session when hang-up is clicked", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    renderWithQuery(<ActiveCallOverlay />);
    screen.getByRole("button", { name: "Hang up" }).click();

    expect(socketSendMock).toHaveBeenCalledWith({
      type: "call.hangup",
      call_id: "call-1",
    });
    expect(useCallStore.getState().phase).toBe("ended");
  });
});
