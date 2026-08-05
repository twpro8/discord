// shared
import { AvatarInitial, type PresenceStatus } from "@/shared/ui/avatar-initial";

// features
import { useServerPresence } from "@/features/presence/model/use-server-presence";

// relative
import { useServerMembers } from "../model/use-server-members";

function Skeleton() {
  return (
    <div className="space-y-2 px-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex animate-pulse items-center gap-3 py-2.5">
          <div className="h-9 w-9 rounded-full bg-muted" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3.5 w-24 rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <p className="px-3 pt-6 text-center text-sm text-muted-foreground">
      No members yet.
    </p>
  );
}

/** Lists a server's members with their live presence status. */
export function ServerMemberList({ serverId }: { serverId: string }) {
  const { data: members = [], isLoading: isLoadingMembers } =
    useServerMembers(serverId);
  const { data: presenceEntries = [] } = useServerPresence(serverId);

  const statusByUserId: Record<string, PresenceStatus> = {};
  for (const entry of presenceEntries)
    statusByUserId[entry.user_id] = entry.status;

  if (isLoadingMembers) return <Skeleton />;
  if (members.length === 0) return <EmptyState />;

  return (
    <div className="space-y-0.5">
      {members.map((member) => {
        const status = statusByUserId[member.user_id];
        return (
          <div
            key={member.id}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50"
          >
            <AvatarInitial username={member.username} status={status} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">
                {member.username}
              </p>
              <p className="truncate text-xs text-muted-foreground capitalize">
                {member.role}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
