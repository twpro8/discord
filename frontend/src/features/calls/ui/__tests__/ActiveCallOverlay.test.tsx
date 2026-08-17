import type { ReactNode } from "react";

import { createTestQueryClient } from "@/testing/render-hook";
import { QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { getFriendsPresence } from "@/features/presence/api/get-friends-presence";
import { socketSend } from "@/features/realtime/model/socket-sender";

import { useCallStore } from "../../model/use-call-store";
import {
  startCameraShare,
  startScreenShare,
  stopVideoShare,
} from "../../model/webrtc-session";
import { ActiveCallOverlay } from "../ActiveCallOverlay";

vi.mock("@/features/realtime/model/socket-sender", () => ({
  socketSend: vi.fn(),
}));
vi.mock("../../model/webrtc-session", () => ({
  setMuted: vi.fn(),
  teardown: vi.fn(),
  startCameraShare: vi.fn(),
  startScreenShare: vi.fn(),
  stopVideoShare: vi.fn(),
}));
vi.mock("@/features/presence/api/get-friends-presence", () => ({
  getFriendsPresence: vi.fn(),
}));

const socketSendMock = vi.mocked(socketSend);
const getFriendsPresenceMock = vi.mocked(getFriendsPresence);
const startCameraShareMock = vi.mocked(startCameraShare);
const startScreenShareMock = vi.mocked(startScreenShare);
const stopVideoShareMock = vi.mocked(stopVideoShare);

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
  return {
    getTracks: () => [],
    getVideoTracks: () => [],
  } as unknown as MediaStream;
}

/** A remote stream whose video track stays live+unmuted no matter what —
 * exactly what a peer's replaceTrack(null) leaves behind on the
 * receiving side (the spec fires no mute/ended event), which is what
 * used to keep the panel mounted on a frozen frame. */
function frozenShareStream(): MediaStream {
  return {
    getTracks: () => [{ kind: "video", readyState: "live", muted: false }],
    getVideoTracks: () => [{ kind: "video", readyState: "live", muted: false }],
  } as unknown as MediaStream;
}

describe("ActiveCallOverlay", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
    socketSendMock.mockClear();
    getFriendsPresenceMock.mockReset();
    getFriendsPresenceMock.mockResolvedValue([]);
    startCameraShareMock.mockReset();
    startCameraShareMock.mockResolvedValue();
    startScreenShareMock.mockReset();
    startScreenShareMock.mockResolvedValue();
    stopVideoShareMock.mockReset();
    stopVideoShareMock.mockResolvedValue();
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

  it("shows the video panel while the peer is sharing video, even with no remote track", () => {
    // The sharing fact arrives over signaling (call.media_state) — not
    // from track events, which never fire for the peer's replaceTrack(null).
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());
    useCallStore.getState().setPeerMediaState(true, false);

    renderWithQuery(<ActiveCallOverlay />);

    expect(screen.getByText("Connected")).toBeInTheDocument();
    expect(document.querySelector("video")).toBeInTheDocument();
  });

  it("collapses to the voice strip when the peer stops sharing video, even though their track still looks live", () => {
    // The regression: a peer's stop uses replaceTrack(null), which the
    // spec leaves invisible on the receiver — the remote video track
    // keeps reporting readyState "live" + unmuted, so the old
    // "does the remote stream have video?" check kept the panel mounted
    // on the frozen last frame. The collapse must come from the signaled
    // call.media_state, not from inspecting the tracks.
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(frozenShareStream());
    useCallStore.getState().setPeerMediaState(true, false);

    renderWithQuery(<ActiveCallOverlay />);
    expect(document.querySelector("video")).toBeInTheDocument();

    act(() => {
      useCallStore.getState().setPeerMediaState(false, false);
    });
    expect(document.querySelector("video")).not.toBeInTheDocument();
  });

  it("shows the voice strip when the peer is not sharing, even if a live remote video track lingers", () => {
    // A stale-but-live remote track (e.g. produced by an earlier share
    // whose stop signal has already been processed) must not by itself
    // open the video panel — the signaled state is the source of truth.
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(frozenShareStream());

    renderWithQuery(<ActiveCallOverlay />);

    expect(document.querySelector("video")).not.toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
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

  it("shows video and screen share toggles once the call is connected", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    renderWithQuery(<ActiveCallOverlay />);

    expect(
      screen.getByRole("button", { name: "Share video" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Share screen" }),
    ).toBeInTheDocument();
  });

  it("hides the video toggles while still ringing", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });

    renderWithQuery(<ActiveCallOverlay />);

    expect(
      screen.queryByRole("button", { name: "Share video" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Share screen" }),
    ).not.toBeInTheDocument();
  });

  it("starts a camera share when Share video is clicked", async () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    renderWithQuery(<ActiveCallOverlay />);
    screen.getByRole("button", { name: "Share video" }).click();

    await vi.waitFor(() => {
      expect(startCameraShareMock).toHaveBeenCalledWith("call-1");
    });
  });

  it("starts a screen share when Share screen is clicked", async () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    renderWithQuery(<ActiveCallOverlay />);
    screen.getByRole("button", { name: "Share screen" }).click();

    await vi.waitFor(() => {
      expect(startScreenShareMock).toHaveBeenCalledWith("call-1");
    });
  });

  it("stops the share (both kinds) via stopVideoShare when the active toggle is re-clicked", async () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());
    useCallStore.getState().setSharingVideo(true);

    renderWithQuery(<ActiveCallOverlay />);
    screen.getByRole("button", { name: "Stop sharing video" }).click();

    await vi.waitFor(() => {
      expect(stopVideoShareMock).toHaveBeenCalled();
    });
  });

  it("renders the self-view video when a share is active", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());
    useCallStore.getState().setSharingVideo(true);

    const { container } = renderWithQuery(<ActiveCallOverlay />);

    // Video panel: the main remote <video> plus the local preview.
    expect(container.querySelectorAll("video")).toHaveLength(2);
  });
});
