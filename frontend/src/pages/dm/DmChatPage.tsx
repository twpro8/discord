// third party
import { useParams, useSearch } from "@tanstack/react-router";

// features
import { DmChatView } from "@/features/chats/ui/DmChatView";

/** Direct message page rendering a conversation by chat id. */
export default function DmChatPage() {
  const { chatId } = useParams({ from: "/home/dms/$chatId" });
  const { peerName, peerId } = useSearch({ from: "/home/dms/$chatId" });

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <DmChatView chatId={chatId} peerName={peerName} peerId={peerId} />
    </div>
  );
}
