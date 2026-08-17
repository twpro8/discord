// react
import { useEffect, useRef } from "react";

// third party
import {
  Mic,
  MicOff,
  MonitorUp,
  PhoneOff,
  Video,
  VideoOff,
} from "lucide-react";
import { toast } from "sonner";

import { cn } from "@/shared/helpers/utils";
// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";

// features
import { useChatDetails } from "@/features/chats/model/use-chat-details";
import { useFriendsPresence } from "@/features/presence/model/use-friends-presence";
import { socketSend } from "@/features/realtime/model/socket-sender";

// relative
import type { CallPhase } from "../model/types";
import { useCallStore } from "../model/use-call-store";
import {
  cameraErrorMessage,
  screenShareErrorMessage,
} from "../model/video-error";
import {
  setMuted,
  startCameraShare,
  startScreenShare,
  stopVideoShare,
  teardown,
} from "../model/webrtc-session";

// How long the "Call ended" state stays visible before auto-resetting to
// idle — long enough to read, short enough not to linger.
const ENDED_DISPLAY_MS = 2_000;

// outgoing_ringing has no static label — it's derived from the peer's
// presence (see statusLabel below): "Waiting…" while they're offline,
// "Ringing…" once we know they're actually reachable to pick up.
const PHASE_LABEL: Partial<Record<CallPhase, string>> = {
  connecting: "Connecting…",
  active: "Connected",
  ended: "Call ended",
};

/** Whether the camera/screen controls make sense on the overlay — only
 * once a call is accepted (a share mid-ring would start negotiating with
 * nobody on the other side yet). The caller can still start a share the
 * instant it flips to "connecting". */
function canShareVideo(phase: CallPhase): boolean {
  return phase === "connecting" || phase === "active";
}

/** Global call overlay for every non-idle phase except incoming-ringing
 * (that has its own modal, IncomingCallModal) — mounted once in
 * HomeLayout so it persists across navigation between chats. Calls are
 * voice-first; the camera and screen-share toggles opt into video
 * mid-call (see webrtc-session.ts). */
export function ActiveCallOverlay() {
  const phase = useCallStore((state) => state.phase);
  const callId = useCallStore((state) => state.callId);
  const chatId = useCallStore((state) => state.chatId);
  const peerId = useCallStore((state) => state.peerId);
  const storedPeerName = useCallStore((state) => state.peerName);
  const isMuted = useCallStore((state) => state.isMuted);
  const isSharingVideo = useCallStore((state) => state.isSharingVideo);
  const isScreenSharing = useCallStore((state) => state.isScreenSharing);
  const peerIsSharingVideo = useCallStore((state) => state.peerIsSharingVideo);
  const peerIsScreenSharing = useCallStore(
    (state) => state.peerIsScreenSharing,
  );
  const localStream = useCallStore((state) => state.localStream);
  const remoteStream = useCallStore((state) => state.remoteStream);
  const errorMessage = useCallStore((state) => state.errorMessage);
  const { data: chatDetails } = useChatDetails(chatId);
  const displayName = chatDetails?.peer_name ?? storedPeerName ?? "Call";

  // Presence is only known for friends (see DmChatView's own use of this
  // hook) — an unresolved status defaults to "Ringing…" below rather
  // than assuming offline, since we genuinely don't know either way.
  const { data: presenceEntries = [] } = useFriendsPresence();
  const peerStatus = presenceEntries.find(
    (entry) => entry.user_id === peerId,
  )?.status;

  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);
  const remoteVideoRef = useRef<HTMLVideoElement | null>(null);
  const localVideoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    // Exactly one of the two remote elements is mounted at a time (the
    // voice strip's <audio> vs the video panel's <video>) — both render
    // the same remoteStream, when their branch is live.
    if (remoteAudioRef.current) {
      remoteAudioRef.current.srcObject = remoteStream;
    }
    if (remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  useEffect(() => {
    if (localVideoRef.current) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream, isSharingVideo, isScreenSharing]);

  useEffect(() => {
    if (phase !== "ended") return;
    const timer = window.setTimeout(() => {
      useCallStore.getState().reset();
    }, ENDED_DISPLAY_MS);
    return () => window.clearTimeout(timer);
  }, [phase]);

  const isVisible =
    phase === "outgoing_ringing" ||
    phase === "connecting" ||
    phase === "active" ||
    phase === "ended";
  if (!isVisible) return null;

  // Whether the video panel makes sense is decided by the *signaled*
  // sharing state (call.media_state from both sides), NOT by inspecting
  // the remote tracks: when a peer stops a share they call
  // replaceTrack(null), which the spec deliberately leaves invisible on
  // the receiving end — the track keeps reporting live+unmuted, so a
  // "does the remote stream have video?" check would keep the panel
  // mounted on a frozen last frame forever. The signal is the only thing
  // that can turn this false promptly and reliably.
  const hasVideo =
    isSharingVideo ||
    isScreenSharing ||
    peerIsSharingVideo ||
    peerIsScreenSharing;

  const handleHangup = () => {
    if (callId) socketSend({ type: "call.hangup", call_id: callId });
    teardown();
    useCallStore.getState().endCall(null);
  };

  const handleToggleMute = () => {
    setMuted(!isMuted);
    useCallStore.getState().toggleMute();
  };

  const handleToggleCamera = async () => {
    if (!callId) return;
    if (isSharingVideo) {
      await stopVideoShare();
      return;
    }
    try {
      await startCameraShare(callId);
    } catch (error) {
      toast.error(cameraErrorMessage(error));
    }
  };

  const handleToggleScreenShare = async () => {
    if (!callId) return;
    if (isScreenSharing) {
      await stopVideoShare();
      return;
    }
    try {
      await startScreenShare(callId);
    } catch (error) {
      toast.error(screenShareErrorMessage(error));
    }
  };

  let statusLabel: string | undefined;
  if (phase === "ended") {
    statusLabel =
      errorMessage === "connection_failed" ? "Call failed" : "Call ended";
  } else if (phase === "outgoing_ringing") {
    statusLabel = peerStatus === "offline" ? "Waiting…" : "Ringing…";
  } else {
    statusLabel = PHASE_LABEL[phase];
  }

  const controls = phase !== "ended" && (
    <>
      <Button
        variant={isMuted ? "secondary" : "ghost"}
        size="icon"
        onClick={handleToggleMute}
        aria-label={isMuted ? "Unmute" : "Mute"}
        className={cn(hasVideo && "bg-black/40 text-white hover:bg-black/60")}
      >
        {isMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
      </Button>
      {canShareVideo(phase) && (
        <Button
          variant={isSharingVideo ? "secondary" : "ghost"}
          size="icon"
          onClick={() => void handleToggleCamera()}
          aria-label={isSharingVideo ? "Stop sharing video" : "Share video"}
          className={cn(hasVideo && "bg-black/40 text-white hover:bg-black/60")}
        >
          {isSharingVideo ? (
            <VideoOff className="h-4 w-4" />
          ) : (
            <Video className="h-4 w-4" />
          )}
        </Button>
      )}
      {canShareVideo(phase) && (
        <Button
          variant={isScreenSharing ? "secondary" : "ghost"}
          size="icon"
          onClick={() => void handleToggleScreenShare()}
          aria-label={isScreenSharing ? "Stop sharing screen" : "Share screen"}
          className={cn(hasVideo && "bg-black/40 text-white hover:bg-black/60")}
        >
          {isScreenSharing ? (
            <MonitorUp className="h-4 w-4 text-destructive" />
          ) : (
            <MonitorUp className="h-4 w-4" />
          )}
        </Button>
      )}
      <Button
        variant="destructive"
        size="icon"
        onClick={handleHangup}
        aria-label="Hang up"
      >
        <PhoneOff className="h-4 w-4" />
      </Button>
    </>
  );

  if (!hasVideo) {
    return (
      <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center">
        <div className="pointer-events-auto flex items-center gap-4 rounded-xl border border-border bg-surface px-4 py-3 shadow-lg">
          <Avatar name={displayName} />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-foreground">
              {displayName}
            </p>
            <p className="text-xs text-muted-foreground">{statusLabel}</p>
          </div>
          {controls}
          {/* Bound to remoteStream via ref rather than a JSX srcObject prop —
              React has no built-in prop for MediaStream objects. */}
          <audio ref={remoteAudioRef} autoPlay className="hidden" />
        </div>
      </div>
    );
  }

  return (
    <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* The remote <video> carries audio too, which is why the voice-only
          strip above needs no separate element when video is live. */}
      <div className="pointer-events-auto relative w-full max-w-2xl overflow-hidden rounded-xl border border-border bg-black shadow-lg">
        <video
          ref={remoteVideoRef}
          autoPlay
          playsInline
          className="aspect-video w-full bg-black object-contain"
        />
        {(isSharingVideo || isScreenSharing) && (
          <video
            ref={localVideoRef}
            muted
            autoPlay
            playsInline
            className={cn(
              "absolute right-3 top-3 h-24 w-36 rounded-lg border border-border bg-black object-cover shadow-md",
              // A camera preview mirrors (their camera and ours are both
              // front-facing); a screen-share preview doesn't.
              !isScreenSharing && "-scale-x-100",
            )}
          />
        )}
        <div className="absolute inset-x-0 top-0 flex items-center gap-2 bg-linear-to-b from-black/60 to-transparent p-3">
          <Avatar name={displayName} className="h-8 w-8 text-sm" />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-white">
              {displayName}
            </p>
            <p className="text-xs text-white/70">{statusLabel}</p>
          </div>
        </div>
        {controls && (
          <div className="absolute inset-x-0 bottom-0 flex items-center justify-center gap-3 bg-linear-to-t from-black/60 to-transparent p-4">
            {controls}
          </div>
        )}
      </div>
    </div>
  );
}
