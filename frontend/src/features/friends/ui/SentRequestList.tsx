// third party
import { Ban } from "lucide-react";

// shared
import { timeAgo } from "@/shared/helpers/utils";

// relative
import type { FriendRequestWithUser } from "../model/types";
import { AvatarInitial } from "./avatar-initial";

function SentItem({
  request,
  disabled,
  onCancel,
}: {
  request: FriendRequestWithUser;
  disabled: boolean;
  onCancel: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">
          {request.username}
        </p>
        <p className="text-xs text-muted-foreground">
          {timeAgo(request.created_at)}
        </p>
      </div>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onCancel(request.id)}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-40"
        aria-label="Cancel friend request"
      >
        <Ban className="h-4 w-4" />
      </button>
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
      No sent requests
    </p>
  );
}

/** Lists sent friend requests with cancel actions. */
export function SentRequestList({
  requests,
  isLoading,
  disabled,
  onCancel,
}: {
  requests: FriendRequestWithUser[];
  isLoading: boolean;
  disabled: boolean;
  onCancel: (id: string) => void;
}) {
  if (isLoading) return <Skeleton />;
  if (requests.length === 0) return <EmptyState />;

  return (
    <div className="space-y-0.5">
      {requests.map((request) => (
        <SentItem
          key={request.id}
          request={request}
          disabled={disabled}
          onCancel={onCancel}
        />
      ))}
    </div>
  );
}
