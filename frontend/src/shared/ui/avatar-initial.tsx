// relative
import { cn } from "../helpers/utils";

/** Aggregate connection status — online (active), away (idle), or offline.
 * Defined here (not in features/presence) since this shared UI component
 * is the lowest common consumer; the presence feature re-exports it. */
export type PresenceStatus = "online" | "away" | "offline";

const STATUS_LABEL: Record<PresenceStatus, string> = {
  online: "Online",
  away: "Away",
  offline: "Offline",
};

const STATUS_DOT_CLASS: Record<PresenceStatus, string> = {
  online: "bg-success",
  away: "bg-warning",
  offline: "bg-text-tertiary",
};

/** Circular avatar showing the first letter of a username, with an
 * optional presence status dot. Status is paired with visually-hidden
 * text — color alone isn't a sufficient signal for three states. */
export function AvatarInitial({
  username,
  status,
}: {
  username: string;
  status?: PresenceStatus;
}) {
  return (
    <div className="relative inline-flex shrink-0">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
        {username.charAt(0).toUpperCase()}
      </div>
      {status && (
        <span
          className={cn(
            "absolute right-0 bottom-0 h-2.5 w-2.5 rounded-full ring-2 ring-surface",
            STATUS_DOT_CLASS[status],
          )}
        >
          <span className="sr-only">{STATUS_LABEL[status]}</span>
        </span>
      )}
    </div>
  );
}
