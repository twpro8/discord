// third party
import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Menu, Users } from "lucide-react";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { AvatarInitial } from "@/shared/ui/avatar-initial";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { useChatMessages } from "../model/use-chat-messages";
import { useSendChatMessage } from "../model/use-send-chat-message";
import { MessageComposer } from "./MessageComposer";
import { MessageList } from "./MessageList";

const HEADER_BUTTON =
  "flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:size-8";

/** Direct message conversation for a chat with a peer. */
export function DmChatView({
  chatId,
  peerName,
}: {
  chatId: string;
  peerName?: string;
}) {
  const navigate = useNavigate();
  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const openServers = useShellDrawer((state) => state.openServers);
  const openFriends = useShellDrawer((state) => state.openFriends);
  const { data: user } = useCurrentUser();
  const { data: messages = [] } = useChatMessages(chatId);
  const sendMutation = useSendChatMessage(chatId);

  const displayName = peerName || "Direct message";

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
            aria-label="Open friends panel"
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

      <div className="shrink-0 p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <MessageComposer
          onSend={(body) => sendMutation.mutate(body)}
          disabled={sendMutation.isPending}
        />
      </div>
    </div>
  );
}
