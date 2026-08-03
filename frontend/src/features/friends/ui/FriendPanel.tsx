// react
import { useState } from "react";

// third party
import { useNavigate } from "@tanstack/react-router";
import { UserPlus } from "lucide-react";

// shared
import { cn } from "@/shared/helpers/utils";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { useCreatePrivateChat } from "@/features/chats/model/use-create-private-chat";
import { useCurrentUser } from "@/features/profile/model/use-current-user";

// relative
import { getFriendPeerId } from "../model/get-friend-peer-id";
import type { FriendRequestWithUser } from "../model/types";
import {
  useAcceptFriendRequest,
  useDeleteFriendRequest,
  useRemoveFriend,
} from "../model/use-friend-mutations";
import { useFriendRequests } from "../model/use-friend-requests";
import { useFriends } from "../model/use-friends";
import { AddFriendModal } from "./AddFriendModal";
import { FriendList } from "./FriendList";
import { PendingRequestList } from "./PendingRequestList";
import { SentRequestList } from "./SentRequestList";

type Tab = "pending" | "sent" | "friends";

const TABS: { key: Tab; label: string }[] = [
  { key: "pending", label: "Pending" },
  { key: "sent", label: "Sent" },
  { key: "friends", label: "Friends" },
];

/** Sidebar panel with tabs for pending, sent, and friends lists. */
export function FriendPanel({ className }: { className?: string }) {
  const [isAddFriendOpen, setIsAddFriendOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("pending");

  const navigate = useNavigate();
  const closeFriends = useShellDrawer((state) => state.closeFriends);
  const { data: user } = useCurrentUser();
  const { incoming, sent, isLoading: isLoadingRequests } = useFriendRequests();
  const { data: friends = [], isLoading: isLoadingFriends } = useFriends();

  const acceptMutation = useAcceptFriendRequest();
  const deleteMutation = useDeleteFriendRequest();
  const removeMutation = useRemoveFriend();
  const createChatMutation = useCreatePrivateChat();

  const handleOpenChat = (friend: FriendRequestWithUser) => {
    if (!user) return;
    const peerId = getFriendPeerId(friend, user.id);
    createChatMutation.mutate(peerId, {
      onSuccess: (chat) => {
        closeFriends();
        navigate({
          to: "/home/dms/$chatId",
          params: { chatId: chat.id },
          search: {
            peerName: friend.username,
          },
        });
      },
    });
  };

  return (
    <aside
      className={cn(
        "flex h-full w-80 flex-col border-l border-border bg-background/95 p-4",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          Friends
        </h2>
        <button
          className="rounded-lg border border-border p-2 text-foreground"
          type="button"
          aria-label="Add friend"
          onClick={() => setIsAddFriendOpen(true)}
        >
          <UserPlus className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 flex gap-1 rounded-lg bg-muted/50 p-0.5">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-background text-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-2 flex-1 overflow-y-auto">
        {activeTab === "pending" && (
          <PendingRequestList
            requests={incoming}
            isLoading={isLoadingRequests}
            disabled={acceptMutation.isPending || deleteMutation.isPending}
            onAccept={(id) => acceptMutation.mutate(id)}
            onDecline={(id) => deleteMutation.mutate(id)}
          />
        )}

        {activeTab === "sent" && (
          <SentRequestList
            requests={sent}
            isLoading={isLoadingRequests}
            disabled={deleteMutation.isPending}
            onCancel={(id) => deleteMutation.mutate(id)}
          />
        )}

        {activeTab === "friends" && (
          <FriendList
            friends={friends}
            isLoading={isLoadingFriends}
            disabled={removeMutation.isPending}
            onOpenChat={handleOpenChat}
            onRemove={(id) => removeMutation.mutate(id)}
          />
        )}
      </div>

      <AddFriendModal
        open={isAddFriendOpen}
        onClose={() => setIsAddFriendOpen(false)}
      />
    </aside>
  );
}
