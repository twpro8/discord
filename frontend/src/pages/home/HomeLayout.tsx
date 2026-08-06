// react
import { useEffect, useState } from "react";

// third party
import { Outlet, useMatchRoute } from "@tanstack/react-router";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { Drawer } from "@/shared/ui/drawer";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { ChannelSidebar } from "@/features/channels/ui/ChannelSidebar";
import { CreateChannelModal } from "@/features/channels/ui/CreateChannelModal";
import { FriendPanel } from "@/features/friends/ui/FriendPanel";
import { RealtimeProvider } from "@/features/realtime/RealtimeProvider";
import { CreateServerModal } from "@/features/servers/ui/CreateServerModal";
import { ServerMemberPanel } from "@/features/servers/ui/ServerMemberPanel";
import { ServerSidebar } from "@/features/servers/ui/ServerSidebar";

/** Authenticated shell with adaptive sidebars and the content outlet. */
export default function HomeLayout() {
  const [isCreateServerOpen, setIsCreateServerOpen] = useState(false);
  const [isCreateChannelOpen, setIsCreateChannelOpen] = useState(false);

  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const {
    isServersOpen,
    isChannelsOpen,
    isFriendsOpen,
    closeServers,
    closeChannels,
    closeFriends,
  } = useShellDrawer();

  const serversInDrawer = isMobile;
  const friendsInDrawer = !isDesktop;

  const matchRoute = useMatchRoute();
  const serverParams = matchRoute({ to: "/home/servers/$serverId" });
  const isServerRoute = serverParams !== false;
  const serverId = isServerRoute ? serverParams.serverId : undefined;
  const channelsInDrawer = isMobile;
  const rightLabel = isServerRoute ? "Members" : "Friends";

  useEffect(() => {
    if (!serversInDrawer) closeServers();
    if (!channelsInDrawer) closeChannels();
    if (!friendsInDrawer) closeFriends();
  }, [
    serversInDrawer,
    channelsInDrawer,
    friendsInDrawer,
    closeServers,
    closeChannels,
    closeFriends,
  ]);

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

        {channelsInDrawer && isServerRoute && serverId ? (
          <Drawer
            open={isChannelsOpen}
            onClose={closeChannels}
            side="left"
            label="Channels"
          >
            <ChannelSidebar
              serverId={serverId}
              onCreateChannel={() => setIsCreateChannelOpen(true)}
            />
          </Drawer>
        ) : isServerRoute && serverId ? (
          <ChannelSidebar
            serverId={serverId}
            onCreateChannel={() => setIsCreateChannelOpen(true)}
          />
        ) : null}

        <main className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </main>

        {friendsInDrawer ? (
          <Drawer
            open={isFriendsOpen}
            onClose={closeFriends}
            side="right"
            label={rightLabel}
          >
            {isServerRoute && serverId ? (
              <ServerMemberPanel serverId={serverId} />
            ) : (
              <FriendPanel />
            )}
          </Drawer>
        ) : isServerRoute && serverId ? (
          <ServerMemberPanel serverId={serverId} />
        ) : (
          <FriendPanel />
        )}

        <CreateServerModal
          open={isCreateServerOpen}
          onClose={() => setIsCreateServerOpen(false)}
        />

        {serverId && (
          <CreateChannelModal
            serverId={serverId}
            open={isCreateChannelOpen}
            onClose={() => setIsCreateChannelOpen(false)}
          />
        )}
      </div>
    </RealtimeProvider>
  );
}
