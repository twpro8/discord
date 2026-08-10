// third party
import { MessagesSquare } from "lucide-react";

// shared
import { timeAgo } from "@/shared/helpers/utils";
import { Avatar } from "@/shared/ui/avatar";

// relative
import type { ChatMessage } from "../model/types";

function MessageRow({ message, name }: { message: ChatMessage; name: string }) {
  return (
    <div className="flex gap-3 px-4 py-2">
      <Avatar name={name} />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <p className="text-sm font-semibold text-foreground">{name}</p>
          <time
            className="text-xs text-muted-foreground"
            dateTime={message.created_at}
          >
            {timeAgo(message.created_at)}
          </time>
        </div>
        <p className="mt-0.5 text-sm text-foreground">{message.body}</p>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center">
      <MessagesSquare className="h-6 w-6 text-muted-foreground" />
      <p className="text-sm font-medium text-foreground">No messages yet</p>
      <p className="text-sm text-muted-foreground">Start the conversation.</p>
    </div>
  );
}

/** Renders chat messages with sender name and timestamp. */
export function MessageList({
  messages,
  currentUserId,
  peerName,
}: {
  messages: ChatMessage[];
  currentUserId?: string;
  peerName: string;
}) {
  if (messages.length === 0) return <EmptyState />;

  return (
    <div className="mx-auto w-full max-w-220 py-4">
      {messages.map((message) => (
        <MessageRow
          key={message.id}
          message={message}
          name={message.sender_id === currentUserId ? "You" : peerName}
        />
      ))}
    </div>
  );
}
