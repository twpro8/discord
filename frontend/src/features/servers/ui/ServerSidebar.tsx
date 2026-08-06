// react
import { useState } from "react";

// third party
import { useNavigate } from "@tanstack/react-router";
import { Compass, Plus, Settings } from "lucide-react";

// shared
import { cn } from "@/shared/helpers/utils";
import { Avatar } from "@/shared/ui/avatar";

// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";
import { SettingsDialog } from "@/features/profile/ui/SettingsDialog";

// relative
import { useServers } from "../model/use-servers";

type ServerSidebarProps = {
  onCreateServerClick: () => void;
  className?: string;
};

/** Server rail sidebar showing user avatar and server icons. */
export function ServerSidebar({
  onCreateServerClick,
  className,
}: ServerSidebarProps) {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const { data: servers = [], isLoading } = useServers();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <aside
      className={cn(
        "flex h-full w-24 flex-col items-center border-r border-border bg-background/95 px-3 py-4",
        className,
      )}
    >
      <button
        type="button"
        aria-label="Open settings"
        onClick={() => setIsSettingsOpen(true)}
        className="flex h-12 w-12 items-center justify-center rounded-2xl transition-transform hover:scale-105 focus-visible:ring-3 focus-visible:ring-ring/50"
      >
        <Avatar
          name={user?.name ?? "U"}
          src={user?.avatar_url}
          className="h-12 w-12 text-lg"
        />
      </button>

      <div className="mt-5 flex w-full items-center flex-col gap-2">
        {isLoading ? (
          <div className="h-12 w-12 animate-pulse rounded-2xl bg-muted" />
        ) : (
          servers.map((server) => (
            <button
              key={server.id}
              className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-muted/50 text-sm font-semibold text-foreground transition hover:bg-muted"
              type="button"
              aria-label={`Open ${server.name}`}
              onClick={() =>
                navigate({
                  to: "/home/servers/$serverId",
                  params: { serverId: server.id },
                })
              }
            >
              {server.name.charAt(0).toUpperCase()}
            </button>
          ))
        )}
      </div>

      <div className="mt-auto flex flex-col gap-2">
        <button
          className="flex h-12 w-12 items-center justify-center rounded-2xl border border-dashed border-border bg-background text-foreground transition hover:bg-muted"
          type="button"
          aria-label="Create server"
          onClick={onCreateServerClick}
        >
          <Plus className="h-5 w-5" />
        </button>
        <button
          className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-background text-foreground transition hover:bg-muted"
          type="button"
          aria-label="Explore servers"
        >
          <Compass className="h-5 w-5" />
        </button>
        <button
          className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-background text-foreground transition hover:bg-muted"
          type="button"
          aria-label="Settings"
          onClick={() => setIsSettingsOpen(true)}
        >
          <Settings className="h-5 w-5" />
        </button>
      </div>

      <SettingsDialog
        open={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </aside>
  );
}
