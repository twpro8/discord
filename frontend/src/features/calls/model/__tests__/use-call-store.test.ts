import { useCallStore } from "../use-call-store";

function fakeStream(): MediaStream {
  return { getTracks: () => [] } as unknown as MediaStream;
}

describe("useCallStore", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
  });

  it("starts idle", () => {
    expect(useCallStore.getState().phase).toBe("idle");
    expect(useCallStore.getState().callId).toBeNull();
  });

  it("beginOutgoingCall sets outgoing_ringing with the call's identity", () => {
    const localStream = fakeStream();
    useCallStore.getState().beginOutgoingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
      localStream,
    });

    const state = useCallStore.getState();
    expect(state.phase).toBe("outgoing_ringing");
    expect(state.direction).toBe("outgoing");
    expect(state.callId).toBe("call-1");
    expect(state.chatId).toBe("chat-1");
    expect(state.peerId).toBe("peer-1");
    expect(state.peerName).toBe("Bob");
    expect(state.localStream).toBe(localStream);
    expect(state.remoteStream).toBeNull();
  });

  it("beginIncomingCall sets incoming_ringing with no local stream yet", () => {
    useCallStore.getState().beginIncomingCall({
      callId: "call-2",
      chatId: "chat-2",
      peerId: "peer-2",
      peerName: "Alice",
    });

    const state = useCallStore.getState();
    expect(state.phase).toBe("incoming_ringing");
    expect(state.direction).toBe("incoming");
    expect(state.localStream).toBeNull();
  });

  it("transitionToConnecting moves to connecting and can attach a fresh local stream", () => {
    useCallStore.getState().beginIncomingCall({
      callId: "call-3",
      chatId: "chat-3",
      peerId: "peer-3",
      peerName: "Alice",
    });
    const localStream = fakeStream();

    useCallStore.getState().transitionToConnecting(localStream);

    const state = useCallStore.getState();
    expect(state.phase).toBe("connecting");
    expect(state.localStream).toBe(localStream);
  });

  it("transitionToConnecting without a stream preserves the existing one", () => {
    const localStream = fakeStream();
    useCallStore.getState().beginOutgoingCall({
      callId: "call-4",
      chatId: "chat-4",
      peerId: "peer-4",
      peerName: "Bob",
      localStream,
    });

    useCallStore.getState().transitionToConnecting();

    expect(useCallStore.getState().localStream).toBe(localStream);
    expect(useCallStore.getState().phase).toBe("connecting");
  });

  it("transitionToActive sets the remote stream and phase", () => {
    const remoteStream = fakeStream();
    useCallStore.getState().transitionToActive(remoteStream);

    expect(useCallStore.getState().phase).toBe("active");
    expect(useCallStore.getState().remoteStream).toBe(remoteStream);
  });

  it("toggleMute flips isMuted", () => {
    expect(useCallStore.getState().isMuted).toBe(false);
    useCallStore.getState().toggleMute();
    expect(useCallStore.getState().isMuted).toBe(true);
    useCallStore.getState().toggleMute();
    expect(useCallStore.getState().isMuted).toBe(false);
  });

  it("endCall moves to ended, clears streams, and keeps peer identity for display", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-5",
      chatId: "chat-5",
      peerId: "peer-5",
      peerName: "Bob",
      localStream: fakeStream(),
    });
    useCallStore.getState().transitionToActive(fakeStream());

    useCallStore.getState().endCall("connection_failed");

    const state = useCallStore.getState();
    expect(state.phase).toBe("ended");
    expect(state.errorMessage).toBe("connection_failed");
    expect(state.localStream).toBeNull();
    expect(state.remoteStream).toBeNull();
    expect(state.peerName).toBe("Bob");
  });

  it("reset returns fully to idle", () => {
    useCallStore.getState().beginOutgoingCall({
      callId: "call-6",
      chatId: "chat-6",
      peerId: "peer-6",
      peerName: "Bob",
      localStream: fakeStream(),
    });

    useCallStore.getState().reset();

    const state = useCallStore.getState();
    expect(state.phase).toBe("idle");
    expect(state.callId).toBeNull();
    expect(state.chatId).toBeNull();
    expect(state.peerId).toBeNull();
    expect(state.peerName).toBeNull();
    expect(state.direction).toBeNull();
    expect(state.localStream).toBeNull();
    expect(state.remoteStream).toBeNull();
    expect(state.errorMessage).toBeNull();
  });
});
