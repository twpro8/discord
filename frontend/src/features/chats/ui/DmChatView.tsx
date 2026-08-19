// third party
import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Menu, Users } from "lucide-react";

// shared
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { Avatar } from "@/shared/ui/avatar";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

import { CallButton } from "@/features/calls/ui/CallButton";
import { useFriendsPresence } from "@/features/presence/model/use-friends-presence";
// features
import { useCurrentUser } from "@/features/profile/model/use-current-user";
import { useSendTyping } from "@/features/typing/model/use-send-typing";
import { useTypingUsers } from "@/features/typing/model/use-typing-users";
import { TypingIndicator } from "@/features/typing/ui/TypingIndicator";

// relative
import { useChatDetails } from "../model/use-chat-details";
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
  peerId,
}: {
  chatId: string;
  peerName?: string;
  peerId?: string;
}) {
  const navigate = useNavigate();
  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const openServers = useShellDrawer((state) => state.openServers);
  const openFriends = useShellDrawer((state) => state.openFriends);
  const { data: user } = useCurrentUser();
  const { data: messages = [] } = useChatMessages(chatId);
  const sendMutation = useSendChatMessage(chatId);
  // The peer only arrives via URL search params on one navigation path
  // (FriendPanel's "message" button) — a refresh, browser back/forward,
  // or a bookmarked link all leave peerId/peerName undefined. GET
  // /chats/{chatId} resolves the peer authoritatively regardless of how
  // the user got here; the props are kept only as an instant optimistic
  // display for the one path that already has them for free, while this
  // query is in flight.
  const { data: chatDetails } = useChatDetails(chatId);
  const resolvedPeerId = chatDetails?.peer_id ?? peerId;
  const resolvedPeerName = chatDetails?.peer_name ?? peerName;
  // Presence is scoped to friends only — a DM peer who isn't (or is no
  // longer) a friend just shows no dot, which is the correct fallback.
  const { data: presenceEntries = [] } = useFriendsPresence();
  const peerStatus = presenceEntries.find(
    (entry) => entry.user_id === resolvedPeerId,
  )?.status;

  const displayName = resolvedPeerName || "Direct message";

  const { notifyTyping, notifyStopTyping } = useSendTyping(chatId);
  const typingUserIds = useTypingUsers(chatId);
  // A DM only ever has one other participant, so any typer is the peer —
  // no name-resolution step needed until a group chat view exists.
  const typingNames = typingUserIds.length > 0 ? [displayName] : [];

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
        <Avatar name={displayName} status={peerStatus} />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-foreground">
            {displayName}
          </p>
          <p className="text-xs text-muted-foreground">Direct message</p>
        </div>
        <CallButton
          userId={user?.id}
          peerId={resolvedPeerId}
          className="ml-auto"
        />
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto">
        <MessageList
          messages={messages}
          currentUserId={user?.id}
          peerName={displayName}
        />
      </div>

      <TypingIndicator names={typingNames} />

      <div className="shrink-0 p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <MessageComposer
          onSend={(body) => sendMutation.mutate(body)}
          disabled={sendMutation.isPending}
          onTyping={notifyTyping}
          onStopTyping={notifyStopTyping}
        />
      </div>
    </div>
  );
}
