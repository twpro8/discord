// react
import { useState } from "react";

// third party
import { Outlet } from "@tanstack/react-router";

import { FriendPanel } from "@/features/friends/ui/FriendPanel";
// features
import { RealtimeProvider } from "@/features/realtime/RealtimeProvider";
import { CreateServerModal } from "@/features/servers/ui/CreateServerModal";
import { ServerSidebar } from "@/features/servers/ui/ServerSidebar";

/** Authenticated shell with server sidebar, content outlet, and friend panel. */
export default function HomeLayout() {
  const [isCreateServerOpen, setIsCreateServerOpen] = useState(false);

  return (
    <RealtimeProvider>
      <div className="flex h-screen w-full bg-canvas">
        <ServerSidebar
          onCreateServerClick={() => setIsCreateServerOpen(true)}
        />

        <main className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </main>

        <FriendPanel />
        <CreateServerModal
          open={isCreateServerOpen}
          onClose={() => setIsCreateServerOpen(false)}
        />
      </div>
    </RealtimeProvider>
  );
}
