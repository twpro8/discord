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
    const [remoteStream] = event.streams;
    if (remoteStream) {
      useCallStore.getState().transitionToActive(remoteStream);
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

/** Adds every track of the local mic stream to the current peer connection. */
export function attachLocalStream(stream: MediaStream): void {
  const connection = pc;
  if (!connection) return;
  stream.getTracks().forEach((track) => connection.addTrack(track, stream));
}

/** Caller side, post-accept: creates and sends the SDP offer. */
export async function createAndSendOffer(callId: string): Promise<void> {
  if (!pc) return;
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  socketSend({ type: "call.offer", call_id: callId, sdp: offer });
}

/** Callee side: applies the caller's offer and sends back an answer. */
export async function handleRemoteOffer(
  callId: string,
  sdp: RTCSessionDescriptionInit,
): Promise<void> {
  if (!pc) return;
  await pc.setRemoteDescription(sdp);
  await flushPendingCandidates();
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  socketSend({ type: "call.answer", call_id: callId, sdp: answer });
}

/** Caller side: applies the callee's answer. */
export async function handleRemoteAnswer(
  sdp: RTCSessionDescriptionInit,
): Promise<void> {
  if (!pc) return;
  await pc.setRemoteDescription(sdp);
  await flushPendingCandidates();
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

/** Enables/disables the local mic track without renegotiating. */
export function setMuted(muted: boolean): void {
  pc?.getSenders().forEach((sender) => {
    if (sender.track) sender.track.enabled = !muted;
  });
}

/** Closes the peer connection and stops every local/remote track — the
 * store's endCall/reset only clear the *references*, this is what
 * actually releases the mic and stops audio playback. */
export function teardown(): void {
  const { localStream, remoteStream } = useCallStore.getState();
  localStream?.getTracks().forEach((track) => track.stop());
  remoteStream?.getTracks().forEach((track) => track.stop());
  pc?.close();
  pc = null;
  pendingRemoteCandidates = [];
}
