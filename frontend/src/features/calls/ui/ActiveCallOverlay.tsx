// react
import { useEffect, useRef } from "react";

// third party
import { Mic, MicOff, PhoneOff } from "lucide-react";

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
import { setMuted, teardown } from "../model/webrtc-session";

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

/** Global call overlay for every non-idle phase except incoming-ringing
 * (that has its own modal, IncomingCallModal) — mounted once in
 * HomeLayout so it persists across navigation between chats. */
export function ActiveCallOverlay() {
  const phase = useCallStore((state) => state.phase);
  const callId = useCallStore((state) => state.callId);
  const chatId = useCallStore((state) => state.chatId);
  const peerId = useCallStore((state) => state.peerId);
  const storedPeerName = useCallStore((state) => state.peerName);
  const isMuted = useCallStore((state) => state.isMuted);
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

  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

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

  const handleHangup = () => {
    if (callId) socketSend({ type: "call.hangup", call_id: callId });
    teardown();
    useCallStore.getState().endCall(null);
  };

  const handleToggleMute = () => {
    setMuted(!isMuted);
    useCallStore.getState().toggleMute();
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
        {phase !== "ended" && (
          <>
            <Button
              variant={isMuted ? "secondary" : "ghost"}
              size="icon"
              onClick={handleToggleMute}
              aria-label={isMuted ? "Unmute" : "Mute"}
            >
              {isMuted ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="destructive"
              size="icon"
              onClick={handleHangup}
              aria-label="Hang up"
            >
              <PhoneOff className="h-4 w-4" />
            </Button>
          </>
        )}
        {/* Bound to remoteStream via ref rather than a JSX srcObject prop —
            React has no built-in prop for MediaStream objects. */}
        <audio ref={audioRef} autoPlay className="hidden" />
      </div>
    </div>
  );
}
