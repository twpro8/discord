// shared
import { cn } from "@/shared/helpers/utils";

// relative
import { useServerMembers } from "../model/use-server-members";
import { ServerMemberList } from "./ServerMemberList";

/** Right-hand panel listing a server's members with live presence. */
export function ServerMemberPanel({
  serverId,
  className,
}: {
  serverId: string;
  className?: string;
}) {
  const { data: members = [] } = useServerMembers(serverId);

  return (
    <aside
      className={cn(
        "flex h-full w-80 flex-col border-l border-border bg-background/95 p-4",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          Members
        </h2>
        <span className="rounded-md bg-muted/50 px-2 py-0.5 text-xs font-medium text-muted-foreground">
          {members.length}
        </span>
      </div>

      <div className="mt-2 flex-1 overflow-y-auto">
        <ServerMemberList serverId={serverId} />
      </div>
    </aside>
  );
}
