// react
import { useCallback, useEffect, useRef, useState } from "react";

// third party
import { toast } from "sonner";

export interface LocalMediaState {
  audioStream: MediaStream | null;
  cameraStream: MediaStream | null;
  screenStream: MediaStream | null;
  muted: boolean;
  cameraEnabled: boolean;
  screenSharing: boolean;
}

/** Manages local media tracks independently: audio (always), camera and screen
 *  share as separate tracks (B-mode). Camera and screen can be active
 *  simultaneously — each produces its own MediaStream/track and consumers
 *  (PeerConnectionManager) add them as separate RTCRtpSenders. */
export function useLocalMedia(active: boolean) {
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [screenStream, setScreenStream] = useState<MediaStream | null>(null);
  const [muted, setMuted] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [screenSharing, setScreenSharing] = useState(false);

  const audioStreamRef = useRef<MediaStream | null>(null);
  const cameraStreamRef = useRef<MediaStream | null>(null);
  const screenStreamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    audioStreamRef.current = audioStream;
  }, [audioStream]);
  useEffect(() => {
    cameraStreamRef.current = cameraStream;
  }, [cameraStream]);
  useEffect(() => {
    screenStreamRef.current = screenStream;
  }, [screenStream]);

  // Acquire audio-only on activation (voice-first, camera off by design).
  useEffect(() => {
    if (!active) return;
    let cancelled = false;
    async function acquireAudio() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        setAudioStream(stream);
      } catch (error) {
        if (cancelled) return;
        console.error("Failed to acquire audio:", error);
        toast.error("Microphone access denied");
      }
    }
    void acquireAudio();
    return () => {
      cancelled = true;
    };
  }, [active]);

  // Cleanup on deactivation.
  useEffect(() => {
    if (active) return;
    audioStreamRef.current?.getTracks().forEach((t) => t.stop());
    cameraStreamRef.current?.getTracks().forEach((t) => t.stop());
    screenStreamRef.current?.getTracks().forEach((t) => t.stop());
    setAudioStream(null);
    setCameraStream(null);
    setScreenStream(null);
    setMuted(false);
    setCameraEnabled(false);
    setScreenSharing(false);
  }, [active]);

  // Stop all on unmount.
  useEffect(() => {
    return () => {
      audioStreamRef.current?.getTracks().forEach((t) => t.stop());
      cameraStreamRef.current?.getTracks().forEach((t) => t.stop());
      screenStreamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const toggleMute = useCallback(() => {
    const track = audioStreamRef.current?.getAudioTracks()[0];
    if (!track) return;
    track.enabled = !track.enabled;
    setMuted(!track.enabled);
  }, []);

  const toggleCamera = useCallback(async () => {
    const existing = cameraStreamRef.current;
    if (existing) {
      const track = existing.getVideoTracks()[0];
      if (track && track.readyState !== "ended") {
        track.enabled = !track.enabled;
        setCameraEnabled(track.enabled);
        return;
      }
      // Track ended — need fresh acquisition.
      existing.getTracks().forEach((t) => t.stop());
      setCameraStream(null);
      cameraStreamRef.current = null;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });
      setCameraStream(stream);
      setCameraEnabled(true);
    } catch (error) {
      console.error("Failed to acquire camera:", error);
      toast.error("Camera access denied");
    }
  }, []);

  const disableCamera = useCallback(() => {
    cameraStreamRef.current?.getTracks().forEach((t) => t.stop());
    setCameraStream(null);
    setCameraEnabled(false);
  }, []);

  const startScreenShare = useCallback(async () => {
    if (screenStreamRef.current) return;
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { displaySurface: "monitor" } as MediaTrackConstraints,
        audio: false,
      });
      const track = stream.getVideoTracks()[0];
      if (!track) return;
      track.onended = () => {
        stream.getTracks().forEach((t) => t.stop());
        setScreenStream(null);
        setScreenSharing(false);
      };
      setScreenStream(stream);
      setScreenSharing(true);
    } catch (error) {
      // User cancelled picker — not an error.
      if ((error as DOMException)?.name === "NotAllowedError") return;
      console.error("Failed to start screen share:", error);
      toast.error("Screen share failed");
    }
  }, []);

  const stopScreenShare = useCallback(() => {
    screenStreamRef.current?.getTracks().forEach((t) => t.stop());
    setScreenStream(null);
    setScreenSharing(false);
  }, []);

  const stopAll = useCallback(() => {
    audioStreamRef.current?.getTracks().forEach((t) => t.stop());
    cameraStreamRef.current?.getTracks().forEach((t) => t.stop());
    screenStreamRef.current?.getTracks().forEach((t) => t.stop());
    setAudioStream(null);
    setCameraStream(null);
    setScreenStream(null);
    setMuted(false);
    setCameraEnabled(false);
    setScreenSharing(false);
  }, []);

  return {
    audioStream,
    cameraStream,
    screenStream,
    muted,
    cameraEnabled,
    screenSharing,
    toggleMute,
    toggleCamera,
    disableCamera,
    startScreenShare,
    stopScreenShare,
    stopAll,
  };
}
