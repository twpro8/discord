// third party
import { Phone } from "lucide-react";

import { getUserChannel } from "@/shared/api/socket";
// shared
import { cn } from "@/shared/helpers/utils";

// relative
import { useOutgoingCall } from "../model/use-outgoing-call";

// Matches DmChatView's HEADER_BUTTON class exactly, for visual
// consistency with the chat header's other icon buttons — kept as a
// local duplicate (a Tailwind class string, not real logic) rather than
// a shared import, since DmChatView mounts this component and importing
// the other way would create a cycle.
const HEADER_BUTTON =
  "flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:size-8 disabled:pointer-events-none disabled:opacity-50";

/** "Call" button for a DM chat header — rings the chat's peer by pushing
 * `call_user` onto the current user's already-joined `user:{id}` Phoenix
 * channel. A no-op while the current user id or the peer id is still
 * unresolved. */
export function CallButton({
  userId,
  peerId,
  className,
}: {
  userId?: string;
  peerId?: string;
  className?: string;
}) {
  const openCall = useOutgoingCall((state) => state.open);

  function handleCall() {
    if (!userId || !peerId) return;

    getUserChannel(userId)
      .push("call_user", { target_user_id: peerId })
      .receive("ok", (response: unknown) => {
        const { call_id } = response as { call_id: string };
        openCall(peerId, call_id);
      })
      .receive("error", (error: unknown) => {
        console.error("Call failed:", error);
      });
  }

  return (
    <button
      onClick={handleCall}
      type="button"
      className={cn(HEADER_BUTTON, className)}
      aria-label="Start voice call"
      title="Start voice call"
    >
      <Phone className="h-4 w-4" />
    </button>
  );
}
