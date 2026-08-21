// react
import { useCallback, useEffect, useRef, useState } from "react";

// shared
import { getCallChannel, leaveCallChannel } from "@/shared/api/socket";

const ICE_SERVERS: RTCIceServer[] = [{ urls: "stun:stun.l.google.com:19302" }];

interface UseWebRTCOptions {
  callId: string | null;
  /** "caller" creates the offer; "callee" waits for it then answers. */
  role: "caller" | "callee";
}

/** Manages an RTCPeerConnection for a 1:1 voice call. Gets the local
 *  microphone stream, exchanges SDP offers/answers and ICE candidates
 *  through the Phoenix `call:*` channel, and exposes the remote audio
 *  stream for playback. Cleans up on unmount or when `callId` clears. */
export function useWebRTC({ callId, role }: UseWebRTCOptions) {
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [connected, setConnected] = useState(false);
  const [muted, setMuted] = useState(false);
  const roleRef = useRef(role);
  roleRef.current = role;

  useEffect(() => {
    if (!callId) return;

    const pc = new RTCPeerConnection({ iceServers: ICE_SERVERS });
    pcRef.current = pc;

    pc.ontrack = (event) => {

      console.log("🔊 ontrack fired");
      console.log("event.streams:", event.streams);
      console.log("event.track:", event.track);

      const stream = event.streams[0] ?? null;

      console.log("remote stream:", stream);
      console.log("audio tracks:", stream?.getAudioTracks());

      setRemoteStream(event.streams[0] ?? null);

    };

    pc.oniceconnectionstatechange = () => {
      const state = pc.iceConnectionState;
      if (state === "connected" || state === "completed") {
        setConnected(true);
      } else if (state === "disconnected" || state === "failed") {
        setConnected(false);
      }
    };

    const channel = getCallChannel(callId);

    let makingOffer = false;

    channel.on("offer", async ({ sdp }: { sdp: RTCSessionDescriptionInit }) => {
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
        await pc.addIceCandidate(new RTCIceCandidate(candidate));
      },
    );

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        channel.push("ice_candidate", {
          candidate: event.candidate.toJSON(),
        });
      }
    };

    pc.onnegotiationneeded = async () => {

      if (roleRef.current !== "caller") return;

      if (makingOffer || pc.signalingState !== "stable") return;
      makingOffer = true;
      try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        channel.push("offer", { sdp: pc.localDescription });
      } finally {
        makingOffer = false;
      }
    };

    let cancelled = false;

    async function start() {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false,
      });
      if (cancelled) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }
      setLocalStream(stream);
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));
    }

    start();

    return () => {
      cancelled = true;
      pc.close();
      pcRef.current = null;
      setRemoteStream(null);
      setLocalStream(null);
      setConnected(false);
      channel.off("offer");
      channel.off("answer");
      channel.off("ice_candidate");
      leaveCallChannel();
    };
  }, [callId]);

  const toggleMute = useCallback(() => {
    const track = localStream?.getAudioTracks()[0];
    if (!track) return;
    track.enabled = !track.enabled;
    setMuted(!track.enabled);
  }, [localStream]);

  const hangup = useCallback(() => {
    pcRef.current?.close();
    localStream?.getTracks().forEach((t) => t.stop());
    pcRef.current = null;
    setRemoteStream(null);
    setLocalStream(null);
    setConnected(false);
    setMuted(false);
    leaveCallChannel();
  }, [localStream]);

  return { localStream, remoteStream, connected, muted, toggleMute, hangup };
}
