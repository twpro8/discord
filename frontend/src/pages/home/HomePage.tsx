// react
import { useState } from "react";

// features
import { FriendPanel } from "@/features/friends/ui/FriendPanel";
import { ProfileCard } from "@/features/profile/ui/ProfileCard";
import { CreateServerModal } from "@/features/servers/ui/CreateServerModal";
import { ServerSidebar } from "@/features/servers/ui/ServerSidebar";

/** Main authenticated page with server sidebar, profile, and friend panel. */
export default function HomePage() {
  const [isCreateServerOpen, setIsCreateServerOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-canvas">
      <ServerSidebar onCreateServerClick={() => setIsCreateServerOpen(true)} />

      <main className="flex flex-1 items-center justify-center px-6 py-10">
        <ProfileCard />
      </main>

      <FriendPanel />
      <CreateServerModal
        open={isCreateServerOpen}
        onClose={() => setIsCreateServerOpen(false)}
      />
    </div>
  );
}
