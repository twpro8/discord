// react
import { useEffect, useRef, useState } from "react";

// shared
import { getRoomChannel, leaveRoomChannel } from "@/shared/api/socket";
import { TURN_URL } from "@/shared/config/env";

const ICE_SERVERS: RTCIceServer[] = TURN_URL
  ? [{ urls: TURN_URL }]
  : [{ urls: "stun:stun.l.google.com:19302" }];
// TODO: Replace with fetch GET /api/v1/calls/turn-credentials for time-limited coturn credentials.

export interface RemotePeerStreams {
  audioStream: MediaStream | null;
  videoStream: MediaStream | null; // camera
  screenStream: MediaStream | null;
}

interface UsePeerConnectionsOptions {
  roomId: string | null;
  role: "caller" | "callee";
  audioStream: MediaStream | null;
  cameraStream: MediaStream | null;
  screenStream: MediaStream | null;
}

/** Manages RTCPeerConnections for a room. Supports group-ready Map<peerId, PC>
 *  but currently operates with a single remote peer (1:1). Each PC has up to
 *  3 senders (audio/video/screen) added independently — B-mode. */
export function usePeerConnections({
  roomId,
  role,
  audioStream,
  cameraStream,
  screenStream,
}: UsePeerConnectionsOptions) {
  const pcsRef = useRef<Map<string, RTCPeerConnection>>(new Map());
  const sendersRef = useRef<
    Map<
      string,
      { audio?: RTCRtpSender; video?: RTCRtpSender; screen?: RTCRtpSender }
    >
  >(new Map());
  const makingOfferRef = useRef<Map<string, boolean>>(new Map());
  const expectingScreenRef = useRef<Set<string>>(new Set());
  const roleRef = useRef(role);
  roleRef.current = role;

  const [remoteStreams, setRemoteStreams] = useState<
    Map<string, RemotePeerStreams>
  >(new Map());
  const [connected, setConnected] = useState(false);
  const connectedRef = useRef(false);

  // Keep latest streams in refs for effects that need them without re-creating PCs.
  const audioStreamRef = useRef(audioStream);
  const cameraStreamRef = useRef(cameraStream);
  const screenStreamRef = useRef(screenStream);
  audioStreamRef.current = audioStream;
  cameraStreamRef.current = cameraStream;
  screenStreamRef.current = screenStream;

  useEffect(() => {
    if (!roomId) return;

    // For 1:1 we use a single placeholder peer id. Group: this will become per-participant.
    const peerId = "remote";

    const pc = new RTCPeerConnection({ iceServers: ICE_SERVERS });
    pcsRef.current.set(peerId, pc);
    sendersRef.current.set(peerId, {});
    makingOfferRef.current.set(peerId, false);

    pc.oniceconnectionstatechange = () => {
      const state = pc.iceConnectionState;
      if (state === "connected" || state === "completed") {
        setConnected(true);
        connectedRef.current = true;
      } else if (state === "disconnected" || state === "failed") {
        setConnected(false);
        connectedRef.current = false;
      }
    };

    pc.ontrack = (event) => {
      const track = event.track;
      setRemoteStreams((prev) => {
        const next = new Map(prev);
        const existing = next.get(peerId) ?? {
          audioStream: null,
          videoStream: null,
          screenStream: null,
        };

        if (track.kind === "audio") {
          const stream = event.streams[0] ?? new MediaStream([track]);
          next.set(peerId, { ...existing, audioStream: stream });
        } else if (track.kind === "video") {
          const expectScreen = expectingScreenRef.current.has(peerId);
          const hasVideo = Boolean(existing.videoStream);
          // Explicit signal authoritative: if peer announced screen share, next video is screen.
          // Fallback to second-video heuristic if no signal (backwards compat).
          const treatAsScreen = expectScreen || hasVideo;
          if (treatAsScreen) {
            const stream = event.streams[0] ?? new MediaStream([track]);
            const screenStream =
              stream === existing.videoStream
                ? new MediaStream([track])
                : stream;
            next.set(peerId, { ...existing, screenStream });
            if (expectScreen) expectingScreenRef.current.delete(peerId);
          } else {
            const stream = event.streams[0] ?? new MediaStream([track]);
            next.set(peerId, { ...existing, videoStream: stream });
          }
        }
        return next;
      });
    };

    const channel = getRoomChannel(roomId);

    channel.on("offer", async ({ sdp }: { sdp: RTCSessionDescriptionInit }) => {
      const makingOffer = makingOfferRef.current.get(peerId);
      if (makingOffer || pc.signalingState === "have-local-offer") {
        await pc.setLocalDescription({ type: "rollback" });
      }
      await pc.setRemoteDescription(new RTCSessionDescription(sdp));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      channel.push("answer", { sdp: pc.localDescription });
    });

    channel.on(
      "answer",
      async ({ sdp }: { sdp: RTCSessionDescriptionInit }) => {
        if (pc.signalingState === "have-local-offer") {
          await pc.setRemoteDescription(new RTCSessionDescription(sdp));
        }
      },
    );

    channel.on(
      "ice_candidate",
      async ({ candidate }: { candidate: RTCIceCandidateInit }) => {
        try {
          await pc.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (e) {
          console.warn("Failed to add ICE candidate", e);
        }
      },
    );

    // Explicit screen share signals — authoritative for demux.
    channel.on("screen_share_started", () => {
      expectingScreenRef.current.add(peerId);
    });
    channel.on("screen_share_ended", () => {
      expectingScreenRef.current.delete(peerId);
      setRemoteStreams((prev) => {
        const next = new Map(prev);
        const existing = next.get(peerId);
        if (existing?.screenStream) {
          existing.screenStream.getTracks().forEach((t) => t.stop());
          next.set(peerId, { ...existing, screenStream: null });
        }
        return next;
      });
    });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        channel.push("ice_candidate", { candidate: event.candidate.toJSON() });
      }
    };

    pc.onnegotiationneeded = async () => {
      // Polite peer: both sides can renegotiate after connected (e.g. callee adds screen).
      const needsInitialGate =
        !connectedRef.current && roleRef.current !== "caller";
      if (needsInitialGate) return;
      if (makingOfferRef.current.get(peerId) || pc.signalingState !== "stable")
        return;
      makingOfferRef.current.set(peerId, true);
      try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        channel.push("offer", { sdp: pc.localDescription });
      } finally {
        makingOfferRef.current.set(peerId, false);
      }
    };

    // Attach existing local tracks at creation time.
    if (audioStreamRef.current) {
      const track = audioStreamRef.current.getAudioTracks()[0];
      if (track) {
        const sender = pc.addTrack(track, audioStreamRef.current);
        const entry = sendersRef.current.get(peerId);
        if (entry) entry.audio = sender;
      }
    }
    if (cameraStreamRef.current) {
      const track = cameraStreamRef.current.getVideoTracks()[0];
      if (track) {
        const sender = pc.addTrack(track, cameraStreamRef.current);
        const entry = sendersRef.current.get(peerId);
        if (entry) entry.video = sender;
      }
    }
    if (screenStreamRef.current) {
      const track = screenStreamRef.current.getVideoTracks()[0];
      if (track) {
        const sender = pc.addTrack(track, screenStreamRef.current);
        const entry = sendersRef.current.get(peerId);
        if (entry) entry.screen = sender;
      }
    }

    return () => {
      channel.off("offer");
      channel.off("answer");
      channel.off("ice_candidate");
      channel.off("screen_share_started");
      channel.off("screen_share_ended");
      pc.close();
      pcsRef.current.delete(peerId);
      sendersRef.current.delete(peerId);
      makingOfferRef.current.delete(peerId);
      expectingScreenRef.current.delete(peerId);
      setRemoteStreams(new Map());
      setConnected(false);
      connectedRef.current = false;
      leaveRoomChannel();
    };
    // roomId only — role/media handled by separate effects via refs/senders.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId]);

  // Sync local tracks to all PCs when streams change (B-mode: 3 independent senders).
  useEffect(() => {
    if (!audioStream) return;
    const track = audioStream.getAudioTracks()[0];
    if (!track) return;
    pcsRef.current.forEach((pc, peerId) => {
      const entry = sendersRef.current.get(peerId);
      if (entry?.audio) {
        void entry.audio.replaceTrack(track);
      } else if (pc.signalingState !== "closed") {
        const sender = pc.addTrack(track, audioStream);
        if (entry) entry.audio = sender;
      }
    });
  }, [audioStream]);

  useEffect(() => {
    // Camera track independently — don't affect screen sender.
    pcsRef.current.forEach((pc, peerId) => {
      const entry = sendersRef.current.get(peerId);
      if (cameraStream) {
        const track = cameraStream.getVideoTracks()[0];
        if (!track) return;
        if (entry?.video) {
          void entry.video.replaceTrack(track);
        } else if (pc.signalingState !== "closed") {
          const sender = pc.addTrack(track, cameraStream);
          if (entry) entry.video = sender;
        }
      } else {
        // Camera disabled — keep sender but disable or remove?
        // For B-mode we keep sender and replace with null to avoid renegotiation flicker,
        // but simpler: keep track enabled=false already handled in useLocalMedia toggle.
        // If stream is null (fully disabled), remove sender if exists.
        if (entry?.video) {
          // If stream null, we stopped tracks — remove sender if no track.
          // Use replaceTrack(null) where supported, else remove.
          // For now just keep sender; remote will see muted.
        }
      }
    });
  }, [cameraStream]);

  useEffect(() => {
    let didPush = false;
    pcsRef.current.forEach((pc, peerId) => {
      const entry = sendersRef.current.get(peerId);
      if (screenStream) {
        const track = screenStream.getVideoTracks()[0];
        if (!track) return;
        if (entry?.screen) {
          void entry.screen.replaceTrack(track);
        } else if (pc.signalingState !== "closed") {
          const sender = pc.addTrack(track, screenStream);
          if (entry) entry.screen = sender;
        }
      } else if (entry?.screen) {
        try {
          pc.removeTrack(entry.screen);
        } catch {
          void entry.screen.replaceTrack(null);
        }
        entry.screen = undefined;
      }
    });
    if (screenStream && !didPush) {
      didPush = true;
      if (roomId)
        getRoomChannel(roomId).push("screen_share_started", { enabled: true });
    } else if (!screenStream && pcsRef.current.size > 0) {
      if (roomId)
        getRoomChannel(roomId).push("screen_share_ended", { enabled: false });
    }
  }, [screenStream, roomId]);

  return { remoteStreams, connected, pcsRef, sendersRef };
}
