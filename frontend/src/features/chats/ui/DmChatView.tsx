// third party
import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";

// shared
import { AvatarInitial } from "@/shared/ui/avatar-initial";

// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { useChatMessages } from "../model/use-chat-messages";
import { useSendChatMessage } from "../model/use-send-chat-message";
import { MessageComposer } from "./MessageComposer";
import { MessageList } from "./MessageList";

/** Direct message conversation for a chat with a peer. */
export function DmChatView({
  chatId,
  peerName,
}: {
  chatId: string;
  peerName?: string;
}) {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const { data: messages = [] } = useChatMessages(chatId);
  const sendMutation = useSendChatMessage(chatId);

  const displayName = peerName || "Direct message";

  return (
    <div className="flex h-full min-h-0 flex-col">
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border px-4">
        <button
          type="button"
          onClick={() => navigate({ to: "/home" })}
          className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          aria-label="Back to home"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <AvatarInitial username={displayName} />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-foreground">
            {displayName}
          </p>
          <p className="text-xs text-muted-foreground">Direct message</p>
        </div>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <MessageList
          messages={messages}
          currentUserId={user?.id}
          peerName={displayName}
        />
      </div>

      <div className="shrink-0 p-4">
        <MessageComposer
          onSend={(body) => sendMutation.mutate(body)}
          disabled={sendMutation.isPending}
        />
      </div>
    </div>
  );
}
