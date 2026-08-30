// react
import { useCallback } from "react";

// relative
import { useLocalMedia } from "./use-local-media";
import { usePeerConnections } from "./use-peer-connections";

interface UseWebRTCOptions {
  callId?: string | null;
  roomId?: string | null;
  /** "caller" creates the offer; "callee" waits for it then answers. */
  role: "caller" | "callee";
}

/** Facade for a room-based call. Unified room for 1:1, group and server voice.
 *  `callId` is kept as alias for `roomId`. Manages local media (audio/camera/screen
 *  as 3 independent tracks — B-mode) and peer connections (Map<peerId, PC> with
 *  3 senders each). Backwards compat: `localStream` == audioStream,
 *  `remoteStream` == first peer audio/video stream. */
export function useWebRTC({ callId, roomId, role }: UseWebRTCOptions) {
  const effectiveRoomId = roomId ?? callId ?? null;
  const active = Boolean(effectiveRoomId);

  const {
    audioStream,
    cameraStream,
    screenStream,
    muted,
    cameraEnabled,
    screenSharing,
    toggleMute,
    toggleCamera,
    startScreenShare,
    stopScreenShare,
    stopAll,
  } = useLocalMedia(active);

  const { remoteStreams, connected, pcsRef } = usePeerConnections({
    roomId: effectiveRoomId,
    role,
    audioStream,
    cameraStream,
    screenStream,
  });

  // Backwards compat aliases: single peer placeholder "remote".
  const firstPeer = remoteStreams.get("remote");
  const remoteStream =
    firstPeer?.audioStream ??
    firstPeer?.videoStream ??
    firstPeer?.screenStream ??
    null;
  const remoteVideoStream = firstPeer?.videoStream ?? null;
  const remoteScreenStream = firstPeer?.screenStream ?? null;
  const localStream = audioStream;

  const hangup = useCallback(() => {
    pcsRef.current.forEach((pc) => pc.close());
    pcsRef.current.clear();
    stopAll();
  }, [pcsRef, stopAll]);

  return {
    // New room/group-ready
    roomId: effectiveRoomId,
    localStream,
    audioStream,
    cameraStream,
    screenStream,
    localVideoStream: cameraStream,
    remoteStreams,
    remoteVideoStream,
    remoteScreenStream,
    remoteStream,
    connected,
    muted,
    cameraEnabled,
    screenSharing,
    toggleMute,
    toggleCamera,
    startScreenShare,
    stopScreenShare,
    hangup,
  };
}
