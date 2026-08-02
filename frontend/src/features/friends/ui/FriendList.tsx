// third party
import { Trash2 } from "lucide-react";

// shared
import { AvatarInitial } from "@/shared/ui/avatar-initial";

// relative
import type { FriendRequestWithUser } from "../model/types";

function FriendItem({
  request,
  disabled,
  onRemove,
}: {
  request: FriendRequestWithUser;
  disabled: boolean;
  onRemove: (id: string) => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">
          {request.username}
        </p>
        <p className="text-xs text-muted-foreground">
          Friend since {new Date(request.updated_at).toLocaleDateString()}
        </p>
      </div>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onRemove(request.id)}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-40"
        aria-label="Remove friend"
      >
        <Trash2 className="h-4 w-4" />
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
      No friends yet. Add some!
    </p>
  );
}

/** Lists friends with remove actions. */
export function FriendList({
  friends,
  isLoading,
  disabled,
  onRemove,
}: {
  friends: FriendRequestWithUser[];
  isLoading: boolean;
  disabled: boolean;
  onRemove: (id: string) => void;
}) {
  if (isLoading) return <Skeleton />;
  if (friends.length === 0) return <EmptyState />;

  return (
    <div className="space-y-0.5">
      {friends.map((friend) => (
        <FriendItem
          key={friend.id}
          request={friend}
          disabled={disabled}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
}
