// third party
import { Check, X } from "lucide-react";

// shared
import { timeAgo } from "@/shared/helpers/utils";
import { Avatar } from "@/shared/ui/avatar";

// relative
import type { FriendRequestWithUser } from "../model/types";

function PendingItem({
  request,
  disabled,
  onAccept,
  onDecline,
}: {
  request: FriendRequestWithUser;
  disabled: boolean;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <Avatar name={request.username} src={request.avatar_url} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">
          {request.username}
        </p>
        <p className="text-xs text-muted-foreground">
          {timeAgo(request.created_at)}
        </p>
      </div>
      <div className="flex shrink-0 gap-1">
        <button
          type="button"
          disabled={disabled}
          onClick={() => onAccept(request.id)}
          className="flex h-7 w-7 items-center justify-center rounded-md bg-green-500/10 text-green-500 transition-colors hover:bg-green-500/20 disabled:opacity-40"
          aria-label="Accept friend request"
        >
          <Check className="h-4 w-4" />
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => onDecline(request.id)}
          className="flex h-7 w-7 items-center justify-center rounded-md bg-red-500/10 text-red-500 transition-colors hover:bg-red-500/20 disabled:opacity-40"
          aria-label="Decline friend request"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-2 px-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex animate-pulse items-center gap-3 py-2.5">
          <div className="h-9 w-9 rounded-full bg-muted" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3.5 w-20 rounded bg-muted" />
            <div className="h-3 w-14 rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <p className="px-3 pt-6 text-center text-sm text-muted-foreground">
      No pending requests
    </p>
  );
}

/** Lists incoming friend requests with accept/decline actions. */
export function PendingRequestList({
  requests,
  isLoading,
  disabled,
  onAccept,
  onDecline,
}: {
  requests: FriendRequestWithUser[];
  isLoading: boolean;
  disabled: boolean;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
}) {
  if (isLoading) return <Skeleton />;
  if (requests.length === 0) return <EmptyState />;

  return (
    <div className="space-y-0.5">
      {requests.map((request) => (
        <PendingItem
          key={request.id}
          request={request}
          disabled={disabled}
          onAccept={onAccept}
          onDecline={onDecline}
        />
      ))}
    </div>
  );
}
