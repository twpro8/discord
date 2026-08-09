import type { ReactNode } from "react";

import { createTestQueryClient } from "@/testing/render-hook";
import { QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { socketSend } from "@/features/realtime/model/socket-sender";

import { useCallStore } from "../../model/use-call-store";
import { getIceServers } from "../../model/use-ice-servers";
import {
  attachLocalStream,
  createPeerConnection,
} from "../../model/webrtc-session";
import { IncomingCallModal } from "../IncomingCallModal";

vi.mock("@/features/realtime/model/socket-sender", () => ({
  socketSend: vi.fn(),
}));
vi.mock("../../model/use-ice-servers", () => ({ getIceServers: vi.fn() }));
vi.mock("../../model/webrtc-session", () => ({
  createPeerConnection: vi.fn(),
  attachLocalStream: vi.fn(),
  teardown: vi.fn(),
}));

const socketSendMock = vi.mocked(socketSend);
const getIceServersMock = vi.mocked(getIceServers);
const createPeerConnectionMock = vi.mocked(createPeerConnection);
const attachLocalStreamMock = vi.mocked(attachLocalStream);

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

describe("IncomingCallModal", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
    socketSendMock.mockClear();
    getIceServersMock.mockReset();
    createPeerConnectionMock.mockClear();
    attachLocalStreamMock.mockClear();
    useCallStore.getState().beginIncomingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
    });
  });

  it("renders nothing outside incoming_ringing", () => {
    useCallStore.getState().reset();
    const { container } = renderWithQuery(<IncomingCallModal />);
    expect(container).toBeEmptyDOMElement();
  });

  it("accept: on mic + ICE success, sends call.accept and moves to connecting", async () => {
    const stream = fakeStream();
    vi.stubGlobal("navigator", {
      ...navigator,
      mediaDevices: { getUserMedia: vi.fn().mockResolvedValue(stream) },
    });
    getIceServersMock.mockResolvedValue([{ urls: "stun:stun.example.com" }]);

    renderWithQuery(<IncomingCallModal />);
    await act(async () => {
      screen.getByRole("button", { name: "Accept" }).click();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(createPeerConnectionMock).toHaveBeenCalled();
    expect(attachLocalStreamMock).toHaveBeenCalledWith(stream);
    expect(socketSendMock).toHaveBeenCalledWith({
      type: "call.accept",
      call_id: "call-1",
    });
    expect(useCallStore.getState().phase).toBe("connecting");

    vi.unstubAllGlobals();
  });

  it("accept: on mic permission denial, sends call.reject instead of a silent hang", async () => {
    vi.stubGlobal("navigator", {
      ...navigator,
      mediaDevices: {
        getUserMedia: vi
          .fn()
          .mockRejectedValue(new DOMException("no", "NotAllowedError")),
      },
    });

    renderWithQuery(<IncomingCallModal />);
    await act(async () => {
      screen.getByRole("button", { name: "Accept" }).click();
      await Promise.resolve();
    });

    expect(socketSendMock).toHaveBeenCalledWith({
      type: "call.reject",
      call_id: "call-1",
    });
    expect(createPeerConnectionMock).not.toHaveBeenCalled();
    expect(useCallStore.getState().phase).toBe("idle");

    vi.unstubAllGlobals();
  });

  it("reject sends call.reject and resets", () => {
    renderWithQuery(<IncomingCallModal />);

    screen.getByRole("button", { name: "Decline" }).click();

    expect(socketSendMock).toHaveBeenCalledWith({
      type: "call.reject",
      call_id: "call-1",
    });
    expect(useCallStore.getState().phase).toBe("idle");
  });
});
