// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import DmChatPage from "@/pages/dm/DmChatPage";

/** Direct message route for a conversation with a peer. */
export const Route = createFileRoute("/home/dms/$chatId")({
  validateSearch: (search: Record<string, unknown>) => ({
    peerName: typeof search.peerName === "string" ? search.peerName : undefined,
  }),
  component: DmChatPage,
});
