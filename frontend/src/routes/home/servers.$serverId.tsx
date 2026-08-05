// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import ServerMembersPage from "@/pages/server/ServerMembersPage";

/** Server members route — a minimal server view scoped to the member
 * roster (see ServerMembersPage for why it's not a channel/chat UI). */
export const Route = createFileRoute("/home/servers/$serverId")({
  component: ServerMembersPage,
});
