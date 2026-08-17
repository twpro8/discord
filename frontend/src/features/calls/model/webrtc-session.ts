// features
import { socketSend } from "@/features/realtime/model/socket-sender";

// relative
import { useCallStore } from "./use-call-store";

// Grace period before a "disconnected" (not yet "failed") connection
// state is treated as a real failure — WebRTC can recover from a brief
// ICE hiccup on its own; only a *sustained* disconnect should end the
// call. "failed"/"closed" are already terminal and act immediately.
const DISCONNECT_GRACE_MS = 5_000;

// Module-level, not store state — an RTCPeerConnection isn't renderable
// data, same rationale as socket-sender.ts keeping the raw WebSocket's
// send function outside any store (see use-call-store.ts's docstring).
let pc: RTCPeerConnection | null = null;
let pendingRemoteCandidates: RTCIceCandidateInit[] = [];

// The single accumulated set of remote tracks the UI binds to. Kept here
// (not the store) as the canonical accumulation point, so that mid-call
// renegotiations can append a video track to an existing voice call.
// Each ontrack pushes a *fresh* MediaStream into the store (never this
// object itself) — see the ontrack handler.
let remoteStream: MediaStream | null = null;

// The stream (camera getUserMedia or display getDisplayMedia) currently
// feeding the video sender, so its tracks can be stopped on switch/stop.
let videoShareStream: MediaStream | null = null;

// Perfect-negotiation state (the polite/impolite idiom from the WebRTC
// perfect-negotiation pattern — adapted here because *either* member can
// add a video track mid-call). Roles are pinned by who started the call:
// the caller (outgoing) is impolite, the callee (incoming) is polite.
// Collisions resolve as: the impolite peer's in-flight offer wins; the
// polite peer rolls back, answers, then re-offers its own addition.
let makingOffer = false;
let isSettingRemoteAnswerPending = false;
let needsRenegotiation = false;

/** Creates the RTCPeerConnection for a call about to start and wires its
 * event handlers. Call once per call attempt, before `attachLocalStream`. */
export function createPeerConnection(iceServers: RTCIceServer[]): void {
  pc = new RTCPeerConnection({ iceServers });
  pendingRemoteCandidates = [];

  pc.onicecandidate = (event) => {
    if (!event.candidate) return;
    const callId = useCallStore.getState().callId;
    if (!callId) return;
    socketSend({
      type: "call.ice_candidate",
      call_id: callId,
      candidate: event.candidate.toJSON(),
    });
  };

  pc.ontrack = (event) => {
    remoteStream ??= new MediaStream();
    if (!remoteStream.getTracks().includes(event.track)) {
      remoteStream.addTrack(event.track);
    }
    const pushToStore = () => {
      // Guard: track 'ended' fires inside teardown, which some paths run
      // after endCall — pushing here would resurrect a dead call into a
      // bogus "active" overlay.
      const phase = useCallStore.getState().phase;
      if (phase !== "connecting" && phase !== "active") return;
      // A fresh object every time so the store's remoteStream reference
      // changes. Zustand subscribers compare with Object.is — mutating
      // the same stream in place would skip the re-render (and re-arming
      // of <video> srcObject), so a peer's mid-call video track (camera/
      // screen share) would never appear on this side.
      useCallStore
        .getState()
        .transitionToActive(new MediaStream(remoteStream!.getTracks()));
    };
    pushToStore();
    // The peer's stopVideoShare -> replaceTrack(null) mutes our copy of
    // the video track in place, invisible to the store; these listeners
    // surface it so the overlay collapses to the voice strip instead of
    // a frozen black frame.
    if (event.track.kind === "video") {
      event.track.addEventListener("mute", pushToStore);
      event.track.addEventListener("unmute", pushToStore);
      event.track.addEventListener("ended", pushToStore);
    }
  };

  pc.onconnectionstatechange = () => {
    if (!pc) return;
    if (pc.connectionState === "failed" || pc.connectionState === "closed") {
      useCallStore.getState().endCall("connection_failed");
      teardown();
      return;
    }
    if (pc.connectionState === "disconnected") {
      window.setTimeout(() => {
        if (pc?.connectionState === "disconnected") {
          useCallStore.getState().endCall("connection_failed");
          teardown();
        }
      }, DISCONNECT_GRACE_MS);
    }
  };
}

/** Adds every track of the local mic stream to the current peer
 * connection (video is added later, on demand, via startCameraShare/
 * startScreenShare). */
export function attachLocalStream(stream: MediaStream): void {
  const connection = pc;
  if (!connection) return;
  stream.getTracks().forEach((track) => connection.addTrack(track, stream));
}

/** Caller side, post-accept: creates and sends the SDP offer. */
export async function createAndSendOffer(callId: string): Promise<void> {
  if (!pc) return;
  makingOffer = true;
  try {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socketSend({ type: "call.offer", call_id: callId, sdp: offer });
  } finally {
    makingOffer = false;
  }
}

/** Applies a remote offer and answers it — works identically for the
 * initial offer and for a mid-call renegotiation (camera/screen share),
 * in either direction, resolving the both-share-simultaneously glare
 * case via the polite/impolite roles above. */
export async function handleRemoteOffer(
  callId: string,
  sdp: RTCSessionDescriptionInit,
): Promise<void> {
  if (!pc) return;
  const polite = useCallStore.getState().direction === "incoming";
  const colliding = makingOffer || pc.signalingState !== "stable";

  if (colliding && !polite) {
    // Impolite peer with an in-flight offer of its own: ours supersedes
    // this colliding one — drop it. The polite side rolls back and
    // re-offers its own addition, so the collision resolves without loss.
    return;
  }
  if (colliding) {
    // Polite peer: yield our in-flight offer to the impolite one's. A
    // rollback is only valid while we actually hold a local offer — if
    // the collision lands between negotiation ticks the session is still
    // stable, and there's nothing to roll back.
    try {
      await pc.setLocalDescription({ type: "rollback" });
    } catch {
      // Already stable — this is a fresh negotiation, not a collision.
    }
  }
  await pc.setRemoteDescription(sdp);
  await flushPendingCandidates();
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  socketSend({ type: "call.answer", call_id: callId, sdp: answer });
  if (colliding) {
    // Our own addition was rolled back with the losing offer — re-offer it
    // now that the session is stable under the impolite peer's offer.
    needsRenegotiation = true;
    await settleRenegotiation(callId);
  }
}

/** Caller side: applies an answer, including the answer to a
 * caller-accepted mid-call renegotiation offer. */
export async function handleRemoteAnswer(
  sdp: RTCSessionDescriptionInit,
): Promise<void> {
  if (!pc) return;
  // signals to settleRenegotiation that a remote answer is mid-flight so
  // it doesn't fire its own offer through it.
  isSettingRemoteAnswerPending = true;
  try {
    await pc.setRemoteDescription(sdp);
  } finally {
    isSettingRemoteAnswerPending = false;
  }
  await flushPendingCandidates();
  const callId = useCallStore.getState().callId;
  if (callId) await settleRenegotiation(callId);
}

/** Applies a remote ICE candidate — trickle ICE, so candidates can arrive
 * before the remote description is set; those are queued and flushed once
 * it is (a standard WebRTC ordering gotcha). */
export async function addRemoteIceCandidate(
  candidate: RTCIceCandidateInit,
): Promise<void> {
  if (!pc) return;
  if (!pc.remoteDescription) {
    pendingRemoteCandidates.push(candidate);
    return;
  }
  await pc.addIceCandidate(candidate);
}

async function flushPendingCandidates(): Promise<void> {
  if (!pc) return;
  const queued = pendingRemoteCandidates;
  pendingRemoteCandidates = [];
  for (const candidate of queued) {
    await pc.addIceCandidate(candidate);
  }
}

/** Enables/disables the local mic track without renegotiating. Video is
 * deliberately untouched — muting a voice-call mute shouldn't kill a
 * screen share (sender.track.enabled mutes video too). */
export function setMuted(muted: boolean): void {
  pc?.getSenders().forEach((sender) => {
    if (sender.track?.kind === "audio") sender.track.enabled = !muted;
  });
}

/** Starts sending the camera to the peer. If the call already carries a
 * video track (screen share), swaps the sender's track in place (no
 * renegotiation); otherwise adds the first video track and renegotiates.
 * The camera capture stream is owned by this module until stopVideoShare
 * (or a switch to screen share) — the UI preview binds to the store's
 * localStream, which receives the camera track. Rejects with the raw
 * getUserMedia error for the caller to format. */
export async function startCameraShare(callId: string): Promise<void> {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  await setVideoShareKind(callId, "camera", stream);
}

/** Starts screen sharing with the same add-or-swap semantics as
 * startCameraShare. Registering an "ended" listener covers the browser's
 * own capture indicator ("Stop sharing" chrome) — the track is already
 * gone by then, so the UI state just needs clearing. */
export async function startScreenShare(callId: string): Promise<void> {
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
  await setVideoShareKind(callId, "screen", stream);
  stream.getVideoTracks()[0]?.addEventListener("ended", () => {
    void stopVideoShare();
  });
}

/** Stops sending any video track (camera or screen) and releases the
 * capture stream, then declares the change over signaling
 * (call.media_state). The peer's UI can't learn about a mid-call stop
 * from track events — replaceTrack(null) deliberately gives the remote
 * no signal — so the collapse of their video panel is driven by the
 * signal, not by their (never-firing) mute/ended listeners. */
export async function stopVideoShare(): Promise<void> {
  const connection = pc;
  if (connection) {
    const videoSender = connection
      .getSenders()
      .find((sender) => sender.track?.kind === "video");
    if (videoSender) await videoSender.replaceTrack(null);
  }
  const localStream = useCallStore.getState().localStream;
  localStream
    ?.getVideoTracks()
    .forEach((track) => localStream.removeTrack(track));
  videoShareStream?.getTracks().forEach((track) => track.stop());
  videoShareStream = null;
  useCallStore.getState().setSharingVideo(false);
  useCallStore.getState().setSharingScreen(false);

  const callId = useCallStore.getState().callId;
  if (callId) {
    socketSend({
      type: "call.media_state",
      call_id: callId,
      video_camera: false,
      video_screen: false,
    });
  }
}

async function setVideoShareKind(
  callId: string,
  kind: "camera" | "screen",
  stream: MediaStream,
): Promise<void> {
  const connection = pc;
  if (!connection) return;

  const [videoTrack] = stream.getVideoTracks();
  if (!videoTrack) {
    stream.getTracks().forEach((track) => track.stop());
    throw new DOMException("No video track available", "NotFoundError");
  }

  const localStream = useCallStore.getState().localStream;
  const videoSender = connection
    .getSenders()
    .find((sender) => sender.track?.kind === "video");

  if (videoSender) {
    // A video transceiver already exists (camera <-> screen switch): swap
    // the transmitted track in place — no renegotiation, and the whole
    // switch is a plain replaceTrack on both peers.
    const previous = videoSender.track;
    await videoSender.replaceTrack(videoTrack);
    if (previous) localStream?.removeTrack(previous);
    localStream?.addTrack(videoTrack);
  } else {
    // First video track of the call: addTrack requires renegotiation so
    // the new transceiver enters both sides' SDP.
    if (localStream) localStream.addTrack(videoTrack);
    connection.addTrack(
      videoTrack,
      localStream ?? new MediaStream([videoTrack]),
    );
    scheduleRenegotiation(callId);
  }

  // Stop the previous source only once the new live source is wired up.
  videoShareStream?.getTracks().forEach((track) => track.stop());
  videoShareStream = stream;

  useCallStore.getState().setSharingVideo(kind === "camera");
  useCallStore.getState().setSharingScreen(kind === "screen");

  // Declare the new state over signaling — the same WS channel as SDP —
  // so the peer's overlay mounts/unmounts its video panel from the
  // signal, not from flaky track events.
  socketSend({
    type: "call.media_state",
    call_id: callId,
    video_camera: kind === "camera",
    video_screen: kind === "screen",
  });
}

/** Queues an SDP renegotiation and kicks it off if the session is idle.
 * Used by the first-video-track path (camera/screen share); the addTrack
 * already happened, so when a collision bounces the negotiation the
 * pending flag keeps it alive to re-offer after the exchange settles. */
function scheduleRenegotiation(callId: string): void {
  needsRenegotiation = true;
  void settleRenegotiation(callId);
}

async function settleRenegotiation(callId: string): Promise<void> {
  if (!pc || !needsRenegotiation) return;
  if (
    makingOffer ||
    isSettingRemoteAnswerPending ||
    pc.signalingState !== "stable"
  ) {
    // An exchange is already in flight — retried at the end of
    // handleRemoteAnswer/handleRemoteOffer, or by the next schedule.
    return;
  }
  needsRenegotiation = false;
  makingOffer = true;
  try {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socketSend({ type: "call.offer", call_id: callId, sdp: offer });
  } finally {
    makingOffer = false;
  }
}

/** Closes the peer connection and stops every local/remote track — the
 * store's endCall/reset only clear the *references*, this is what
 * actually releases the mic/camera/display and stops audio/video
 * playback. */
export function teardown(): void {
  const { localStream, remoteStream: storeRemote } = useCallStore.getState();
  videoShareStream?.getTracks().forEach((track) => track.stop());
  videoShareStream = null;
  localStream?.getTracks().forEach((track) => track.stop());
  storeRemote?.getTracks().forEach((track) => track.stop());
  pc?.close();
  pc = null;
  pendingRemoteCandidates = [];
  remoteStream = null;
  makingOffer = false;
  isSettingRemoteAnswerPending = false;
  needsRenegotiation = false;
  useCallStore.getState().setSharingVideo(false);
  useCallStore.getState().setSharingScreen(false);
}
