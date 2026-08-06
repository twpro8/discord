// react
import { useState } from "react";

// third party
import { Hash, Plus } from "lucide-react";

// shared
import { cn } from "@/shared/helpers/utils";

// relative
import { useChannels } from "../model/use-channels";

function Skeleton() {
  return (
    <div className="space-y-1">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="flex animate-pulse items-center gap-2.5 px-2.5 py-2"
        >
          <div className="h-4 w-4 rounded bg-muted" />
          <div className="h-3.5 w-28 rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 px-4 pt-8 text-center">
      <p className="text-sm text-muted-foreground">No channels yet.</p>
      <button
        type="button"
        onClick={onCreate}
        className="rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/80"
      >
        Create channel
      </button>
    </div>
  );
}

/** Context sidebar listing a server's channels with a create entry point. */
export function ChannelSidebar({
  serverId,
  onCreateChannel,
  className,
}: {
  serverId: string;
  onCreateChannel: () => void;
  className?: string;
}) {
  const [activeChannelId, setActiveChannelId] = useState<string | null>(null);
  const { data: channels = [], isLoading } = useChannels(serverId);

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r border-border bg-surface",
        className,
      )}
    >
      <div className="flex items-center justify-between px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          Channels
        </h2>
        <button
          type="button"
          onClick={onCreateChannel}
          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-surface-hover hover:text-foreground"
          aria-label="Create channel"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {isLoading ? (
          <Skeleton />
        ) : channels.length === 0 ? (
          <EmptyState onCreate={onCreateChannel} />
        ) : (
          <div className="space-y-0.5">
            {channels.map((channel) => (
              <button
                key={channel.id}
                type="button"
                onClick={() => setActiveChannelId(channel.id)}
                className={cn(
                  "flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition-colors",
                  activeChannelId === channel.id
                    ? "bg-accent-subtle text-text-primary"
                    : "text-muted-foreground hover:bg-surface-hover hover:text-foreground",
                )}
              >
                <Hash className="h-4 w-4 shrink-0" />
                <span className="min-w-0 truncate">{channel.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
