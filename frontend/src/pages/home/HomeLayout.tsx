// react
import { useEffect, useState } from "react";

// third party
import { Outlet } from "@tanstack/react-router";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { Drawer } from "@/shared/ui/drawer";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { FriendPanel } from "@/features/friends/ui/FriendPanel";
import { RealtimeProvider } from "@/features/realtime/RealtimeProvider";
import { CreateServerModal } from "@/features/servers/ui/CreateServerModal";
import { ServerSidebar } from "@/features/servers/ui/ServerSidebar";

/** Authenticated shell with adaptive sidebars and the content outlet. */
export default function HomeLayout() {
  const [isCreateServerOpen, setIsCreateServerOpen] = useState(false);

  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const { isServersOpen, isFriendsOpen, closeServers, closeFriends } =
    useShellDrawer();

  const serversInDrawer = isMobile;
  const friendsInDrawer = !isDesktop;

  useEffect(() => {
    if (!serversInDrawer) closeServers();
    if (!friendsInDrawer) closeFriends();
  }, [serversInDrawer, friendsInDrawer, closeServers, closeFriends]);

  return (
    <RealtimeProvider>
      <div className="flex h-dvh w-full overflow-hidden bg-canvas">
        {serversInDrawer ? (
          <Drawer
            open={isServersOpen}
            onClose={closeServers}
            side="left"
            label="Servers"
          >
            <ServerSidebar
              onCreateServerClick={() => setIsCreateServerOpen(true)}
            />
          </Drawer>
        ) : (
          <ServerSidebar
            onCreateServerClick={() => setIsCreateServerOpen(true)}
          />
        )}

        <main className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </main>

        {friendsInDrawer ? (
          <Drawer
            open={isFriendsOpen}
            onClose={closeFriends}
            side="right"
            label="Friends"
          >
            <FriendPanel />
          </Drawer>
        ) : (
          <FriendPanel />
        )}

        <CreateServerModal
          open={isCreateServerOpen}
          onClose={() => setIsCreateServerOpen(false)}
        />
      </div>
    </RealtimeProvider>
  );
}
