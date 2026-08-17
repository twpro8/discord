import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// features
import { setSocketSend } from "@/features/realtime/model/socket-sender";

// relative
import { useCallStore } from "../use-call-store";
import {
  createPeerConnection,
  startCameraShare,
  stopVideoShare,
  teardown,
} from "../webrtc-session";

interface FakePc {
  onicecandidate: unknown;
  onconnectionstatechange: unknown;
  ontrack: ((event: unknown) => void) | null;
  close: ReturnType<typeof vi.fn>;
}

interface FakeTrack {
  kind: "audio" | "video";
  readyState: string;
  muted: boolean;
  stop: ReturnType<typeof vi.fn>;
  addEventListener: ReturnType<typeof vi.fn>;
}

const pcInstances: FakePc[] = [];

function createFakeTrack(kind: "audio" | "video") {
  const listeners = new Map<string, Array<() => void>>();
  const track: FakeTrack = {
    kind,
    readyState: "live",
    muted: false,
    stop: vi.fn(),
    addEventListener: vi.fn((type: string, callback: () => void) => {
      const bucket = listeners.get(type) ?? [];
      bucket.push(callback);
      listeners.set(type, bucket);
    }),
  };
  const emit = (type: string) => listeners.get(type)?.forEach((cb) => cb());
  return { track, emit };
}

function fakeMediaStream(tracks: FakeTrack[] = []) {
  const list: FakeTrack[] = [...tracks];
  return {
    getTracks: () => [...list],
    getAudioTracks: () => list.filter((t) => t.kind === "audio"),
    getVideoTracks: () => list.filter((t) => t.kind === "video"),
    addTrack: vi.fn((track: FakeTrack) => {
      if (!list.includes(track)) list.push(track);
    }),
    removeTrack: vi.fn((track: FakeTrack) => {
      const index = list.indexOf(track);
      if (index >= 0) list.splice(index, 1);
    }),
  };
}

const RtcPeerConnectionMock = vi.fn(function (this: FakePc) {
  this.onicecandidate = null;
  this.onconnectionstatechange = null;
  this.ontrack = null;
  this.close = vi.fn();
  pcInstances.push(this);
});

function MediaStreamStub(
  tracks?: FakeTrack[],
): ReturnType<typeof fakeMediaStream> {
  return fakeMediaStream(tracks ?? []);
}
const MediaStreamMock = vi.fn(MediaStreamStub);

describe("webrtc-session ontrack merging", () => {
  beforeEach(() => {
    useCallStore.getState().reset();
    pcInstances.length = 0;
    RtcPeerConnectionMock.mockClear();
    MediaStreamMock.mockClear();
    vi.stubGlobal("RTCPeerConnection", RtcPeerConnectionMock);
    vi.stubGlobal("MediaStream", MediaStreamMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    pcInstances.length = 0;
  });

  it("surfaces a mid-call video track as a fresh store stream containing all tracks", () => {
    createPeerConnection([]);
    // Real flow: phase is "connecting" when the first inbound track lands,
    // which ontrack promotes to "active" — mirror that before firing.
    useCallStore.getState().transitionToConnecting();
    const pc = pcInstances[0];
    const audio = createFakeTrack("audio");
    const video = createFakeTrack("video");

    pc.ontrack?.({ track: audio.track });
    const first = useCallStore.getState().remoteStream;
    expect(useCallStore.getState().phase).toBe("active");
    expect(first?.getTracks()).toEqual([audio.track]);

    // The bug this guards: merging the video track into the SAME stream
    // object kept the store's reference unchanged, so Zustand's Object.is
    // comparison skipped the re-render and the <video> never re-armed its
    // srcObject — the peer's share was invisible on this side.
    pc.ontrack?.({ track: video.track });
    const second = useCallStore.getState().remoteStream;
    expect(second).not.toBe(first);
    expect(second?.getTracks()).toEqual([audio.track, video.track]);
  });

  it("re-pushes a fresh stream when the peer's video track mutes (share stopped)", () => {
    createPeerConnection([]);
    useCallStore.getState().transitionToConnecting();
    const pc = pcInstances[0];
    const audio = createFakeTrack("audio");
    const video = createFakeTrack("video");
    pc.ontrack?.({ track: audio.track });
    pc.ontrack?.({ track: video.track });

    const beforeMute = useCallStore.getState().remoteStream;
    video.track.muted = true;
    video.emit("mute");

    // A new reference lets the overlay recompute remoteHasVideo and
    // collapse from the video panel to the voice strip.
    const afterMute = useCallStore.getState().remoteStream;
    expect(afterMute).not.toBe(beforeMute);
    expect(
      afterMute
        ?.getVideoTracks()
        .some((track) => (track as unknown as FakeTrack).muted),
    ).toBe(true);

    const beforeUnmute = afterMute;
    video.track.muted = false;
    video.emit("unmute");
    expect(useCallStore.getState().remoteStream).not.toBe(beforeUnmute);
  });

  it("does not resurrect an ended call when tracks stop firing ended", () => {
    createPeerConnection([]);
    useCallStore.getState().transitionToConnecting();
    const pc = pcInstances[0];
    const audio = createFakeTrack("audio");
    const video = createFakeTrack("video");
    pc.ontrack?.({ track: audio.track });
    pc.ontrack?.({ track: video.track });

    // The connection_failed path runs endCall BEFORE teardown stops the
    // tracks — the resulting 'ended' events must not re-flip the store.
    useCallStore.getState().endCall("connection_failed");
    expect(useCallStore.getState().phase).toBe("ended");

    video.track.muted = true;
    video.emit("ended");

    expect(useCallStore.getState().phase).toBe("ended");
    expect(useCallStore.getState().remoteStream).toBeNull();
  });
});

describe("video share signaling (call.media_state)", () => {
  let sendSpy: (data: unknown) => void;

  interface ShareAwarePc extends FakePc {
    addTrack: ReturnType<typeof vi.fn>;
    getSenders: () => Array<{
      track: FakeTrack | null;
      replaceTrack: ReturnType<typeof vi.fn>;
    }>;
    signalingState: string;
  }

  beforeEach(() => {
    useCallStore.getState().reset();
    pcInstances.length = 0;
    RtcPeerConnectionMock.mockClear();
    MediaStreamMock.mockClear();
    vi.stubGlobal("RTCPeerConnection", RtcPeerConnectionMock);
    vi.stubGlobal("MediaStream", MediaStreamMock);
    sendSpy = vi.fn();
    setSocketSend(sendSpy);
  });

  afterEach(() => {
    teardown();
    setSocketSend(() => {});
    vi.unstubAllGlobals();
    pcInstances.length = 0;
  });

  it("declares camera sharing over signaling once the share starts", async () => {
    createPeerConnection([]);
    useCallStore.getState().beginIncomingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
    });
    const localStream = fakeMediaStream([createFakeTrack("audio").track]);
    useCallStore
      .getState()
      .transitionToConnecting(localStream as unknown as MediaStream);
    const pc = pcInstances[0] as unknown as ShareAwarePc;
    pc.addTrack = vi.fn();
    pc.getSenders = () => [];
    // Not "stable", so settleRenegotiation bails before createOffer — this
    // test owns the signaling declaration, not the SDP negotiation.
    pc.signalingState = "connecting";
    const cameraTrack = createFakeTrack("video").track;
    vi.stubGlobal("navigator", {
      mediaDevices: {
        getUserMedia: vi.fn().mockResolvedValue({
          getTracks: () => [cameraTrack],
          getVideoTracks: () => [cameraTrack],
        }),
      },
    });

    await startCameraShare("call-1");

    expect(pc.addTrack).toHaveBeenCalled();
    expect(sendSpy).toHaveBeenCalledTimes(1);
    expect(sendSpy).toHaveBeenCalledWith({
      type: "call.media_state",
      call_id: "call-1",
      video_camera: true,
      video_screen: false,
    });
    expect(useCallStore.getState().isSharingVideo).toBe(true);
  });

  it("declares the stop over signaling once sharing ends", async () => {
    createPeerConnection([]);
    const localStream = fakeMediaStream([createFakeTrack("audio").track]);
    useCallStore.getState().beginIncomingCall({
      callId: "call-1",
      chatId: "chat-1",
      peerId: "peer-1",
      peerName: "Bob",
    });
    useCallStore
      .getState()
      .transitionToConnecting(localStream as unknown as MediaStream);
    useCallStore.getState().setSharingVideo(true);
    const pc = pcInstances[0] as unknown as ShareAwarePc;
    const videoTrack = createFakeTrack("video").track;
    const sender = {
      track: videoTrack,
      replaceTrack: vi.fn().mockResolvedValue(undefined),
    };
    pc.getSenders = () => [sender];

    await stopVideoShare();

    expect(sender.replaceTrack).toHaveBeenCalledWith(null);
    expect(sendSpy).toHaveBeenCalledTimes(1);
    expect(sendSpy).toHaveBeenCalledWith({
      type: "call.media_state",
      call_id: "call-1",
      video_camera: false,
      video_screen: false,
    });
    expect(useCallStore.getState().isSharingVideo).toBe(false);
    expect(useCallStore.getState().isScreenSharing).toBe(false);
  });
});
