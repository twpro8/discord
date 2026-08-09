// third party
import { Phone } from "lucide-react";
import { toast } from "sonner";

// shared
import { cn } from "@/shared/helpers/utils";

// features
import { useCallStore } from "@/features/calls/model/use-call-store";
import { useStartCall } from "@/features/calls/model/use-start-call";

// Matches DmChatView's HEADER_BUTTON class exactly, for visual
// consistency with the chat header's other icon buttons — kept as a
// local duplicate (a Tailwind class string, not real logic) rather than
// a shared import, since DmChatView mounts this component and importing
// the other way would create a cycle.
const HEADER_BUTTON =
  "flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:size-8 disabled:pointer-events-none disabled:opacity-50";

/** "Call" button for a DM chat header — starts an outgoing call to the
 * chat's peer. Disabled only while already in a call or when this
 * browser/context doesn't support WebRTC (e.g. no getUserMedia, or an
 * insecure non-HTTPS/non-localhost origin) — deliberately NOT disabled
 * just because `peerId` hasn't resolved yet. DmChatView resolves the
 * peer from chat details (an async query) with the URL's `peerId`
 * search param as a fallback; navigating here directly (a bookmarked
 * link, a pasted URL with no search params, or just a slow first
 * paint) can leave both unresolved for a moment. Gating `disabled` on
 * that would flicker the button through a disabled state — which,
 * combined with `disabled:opacity-50` on an already-muted icon, is
 * easy to misread as "the button doesn't appear at all" — for a
 * purely timing-dependent reason that has nothing to do with whether
 * calling is actually possible right now. The click handler checks
 * for a resolved peer instead, so a click during that gap fails loudly
 * (a toast) rather than either silently doing nothing or appearing
 * unavailable.
 * The support check is re-evaluated per render (not hoisted to module
 * scope) so it stays accurate if globals are ever stubbed/changed after
 * load — notably in tests. */
export function CallButton({
  chatId,
  peerId,
  peerName,
  className,
}: {
  chatId: string;
  peerId?: string;
  peerName: string;
  className?: string;
}) {
  const phase = useCallStore((state) => state.phase);
  const { startCall } = useStartCall();

  const isCallingSupported =
    Boolean(window.RTCPeerConnection) &&
    Boolean(navigator.mediaDevices?.getUserMedia);
  const disabled = phase !== "idle" || !isCallingSupported;

  return (
    <button
      type="button"
      onClick={() => {
        if (!peerId) {
          toast.error(
            "Still loading this chat — try calling again in a moment.",
          );
          return;
        }
        void startCall(chatId, peerId, peerName);
      }}
      disabled={disabled}
      className={cn(HEADER_BUTTON, className)}
      aria-label="Start voice call"
      title={
        isCallingSupported
          ? "Start voice call"
          : "Voice calls aren't supported in this browser"
      }
    >
      <Phone className="h-4 w-4" />
    </button>
  );
}
