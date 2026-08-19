// third party
import { Phone } from "lucide-react";

// shared
import { cn } from "@/shared/helpers/utils";

// Matches DmChatView's HEADER_BUTTON class exactly, for visual
// consistency with the chat header's other icon buttons — kept as a
// local duplicate (a Tailwind class string, not real logic) rather than
// a shared import, since DmChatView mounts this component and importing
// the other way would create a cycle.
const HEADER_BUTTON =
  "flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:size-8 disabled:pointer-events-none disabled:opacity-50";

/** Disabled "Call" button for a DM chat header. Calls were removed from
 * the app, so this is a visual placeholder only — kept in the header for
 * layout consistency until a call feature is built out again. */
export function CallButton({ className }: { className?: string }) {
  return (
    <button
      type="button"
      disabled
      className={cn(HEADER_BUTTON, className)}
      aria-label="Start voice call"
      title="Voice calls aren't available"
    >
      <Phone className="h-4 w-4" />
    </button>
  );
}
