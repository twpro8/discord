// third party
import { useNavigate, useParams } from "@tanstack/react-router";
import { ArrowLeft, Menu, Users } from "lucide-react";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { useServers } from "@/features/servers/model/use-servers";

const HEADER_BUTTON =
  "flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:size-8";

/**
 * Server view placeholder: the member roster lives in the right-hand members
 * panel (HomeLayout), and a channel/chat UI doesn't exist yet, so the middle
 * stays empty apart from the navigation header.
 */
export default function ServerMembersPage() {
  const { serverId } = useParams({ from: "/home/servers/$serverId" });
  const navigate = useNavigate();
  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const openServers = useShellDrawer((state) => state.openServers);
  const openFriends = useShellDrawer((state) => state.openFriends);
  const { data: servers = [] } = useServers();
  const server = servers.find((s) => s.id === serverId);
  const displayName = server?.name ?? "Server";

  return (
    <div className="flex h-full min-h-0 flex-col">
      <header className="flex min-h-14 shrink-0 items-center gap-3 border-b border-border px-3 pt-[env(safe-area-inset-top)] lg:px-4">
        {isMobile && (
          <button
            type="button"
            onClick={openServers}
            className={HEADER_BUTTON}
            aria-label="Open server menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}
        {!isDesktop && (
          <button
            type="button"
            onClick={openFriends}
            className={HEADER_BUTTON}
            aria-label="Open members panel"
          >
            <Users className="h-5 w-5" />
          </button>
        )}
        {isDesktop && (
          <button
            type="button"
            onClick={() => navigate({ to: "/home" })}
            className={HEADER_BUTTON}
            aria-label="Back to home"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
        )}
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-foreground">
            {displayName}
          </p>
        </div>
      </header>
    </div>
  );
}
