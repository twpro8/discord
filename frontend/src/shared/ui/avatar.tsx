// relative
import { cn } from "../helpers/utils";

/** Aggregate connection status — online (active), away (idle), or offline. */
export type AvatarStatus = "online" | "away" | "offline";

const STATUS_LABEL: Record<AvatarStatus, string> = {
  online: "Online",
  away: "Away",
  offline: "Offline",
};

const STATUS_DOT_CLASS: Record<AvatarStatus, string> = {
  online: "bg-success",
  away: "bg-warning",
  offline: "bg-text-tertiary",
};

/** Circular avatar showing the user's image when set, otherwise the first
 * letter of their name, with an optional presence status dot. `className`
 * overrides the default sizing (e.g. `h-12 w-12 text-lg`). */
export function Avatar({
  name,
  src,
  status,
  className,
}: {
  name: string;
  src?: string | null;
  status?: AvatarStatus;
  className?: string;
}) {
  const circle = cn(
    "flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/10 text-sm font-semibold text-primary",
    className,
  );

  return (
    <div className="relative inline-flex shrink-0">
      {src ? (
        <img src={src} alt={name} className={circle} />
      ) : (
        <div className={circle}>{name.charAt(0).toUpperCase()}</div>
      )}
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
