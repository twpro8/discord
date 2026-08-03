// third party
import { Menu, Users } from "lucide-react";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { ProfileCard } from "@/features/profile/ui/ProfileCard";

const HEADER_BUTTON =
  "flex size-10 items-center justify-center gap-2 rounded-md text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground";

/** Home landing content showing the current user's profile. */
export default function HomeIndex() {
  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const openServers = useShellDrawer((state) => state.openServers);
  const openFriends = useShellDrawer((state) => state.openFriends);

  return (
    <div className="flex flex-1 flex-col">
      {!isDesktop && (
        <header className="flex min-h-14 shrink-0 items-center gap-2 border-b border-border px-3 pt-[env(safe-area-inset-top)]">
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
          <button type="button" onClick={openFriends} className={HEADER_BUTTON}>
            <Users className="h-5 w-5" />
            Friends
          </button>
        </header>
      )}

      <div className="flex flex-1 items-center justify-center px-6 py-10">
        <ProfileCard />
      </div>
    </div>
  );
}
