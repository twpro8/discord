import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Search, Users } from "lucide-react";
import { Avatar } from "@/components/Avatar";
import { GROUP_CHATS, DIRECT_CHATS } from "@/data";
import type { ChatEntry } from "@/types";

interface ChatListProps {
    activeChatId: string | null;
    onChatSelect: (id: string) => void;
}

function ChatRow({ chat, active, onClick }: {
    chat: ChatEntry;
    active: boolean;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className="w-full flex items-center gap-2.5 px-2 py-2 rounded-lg transition-colors text-left"
            style={{ backgroundColor: active ? "var(--surface1)" : "transparent" }}
            onMouseEnter={(e) => {
                if (!active)
                    (e.currentTarget as HTMLElement).style.backgroundColor =
                        "var(--surface0)";
            }}
            onMouseLeave={(e) => {
                if (!active)
                    (e.currentTarget as HTMLElement).style.backgroundColor =
                        "transparent";
            }}
        >
            <div className="relative">
                <Avatar
                    initials={chat.initials}
                    color={chat.color}
                    size="md"
                    status={!chat.isGroup ? chat.status : undefined}
                />
                {chat.isGroup && (
                    <span
                        className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: "var(--surface2)" }}
                    >
            <Users size={8} style={{ color: "var(--overlay1)" }} />
          </span>
                )}
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between gap-1">
          <span
              className="text-sm truncate"
              style={{
                  color: "var(--text)",
                  fontWeight: chat.unread ? 600 : 400,
              }}
          >
            {chat.name}
          </span>
                    <span
                        className="text-[10px] shrink-0"
                        style={{ color: "var(--overlay1)" }}
                    >
            {chat.time}
          </span>
                </div>

                <div className="flex items-center justify-between gap-1">
          <span
              className="text-xs truncate"
              style={{ color: "var(--overlay1)" }}
          >
            {chat.lastMessage}
          </span>
                    {chat.unread > 0 && (
                        <span
                            className="shrink-0 min-w-[18px] h-[18px] rounded-full flex items-center justify-center text-[10px] font-semibold px-1"
                            style={{ backgroundColor: "var(--mauve)", color: "var(--base)" }}
                        >
              {chat.unread}
            </span>
                    )}
                </div>
            </div>
        </button>
    );
}

export function ChatList({ activeChatId, onChatSelect }: ChatListProps) {
    return (
        <>
            {/* Search header */}
            <div
                className="px-4 py-3 shrink-0"
                style={{ borderBottom: "1px solid var(--surface1)" }}
            >
                <div
                    className="flex items-center gap-2 rounded-md px-2 py-1.5"
                    style={{ backgroundColor: "var(--surface0)" }}
                >
                    <Search size={13} style={{ color: "var(--overlay1)" }} />
                    <span className="text-xs" style={{ color: "var(--overlay1)" }}>
            Find a conversation...
          </span>
                </div>
            </div>

            <ScrollArea className="flex-1 min-h-0 px-2 py-3">
                <p
                    className="text-[10px] font-semibold tracking-wider px-2 mb-1"
                    style={{ color: "var(--overlay1)" }}
                >
                    GROUP CHATS
                </p>
                <div className="space-y-0.5 mb-3">
                    {GROUP_CHATS.map((chat) => (
                        <ChatRow
                            key={chat.id}
                            chat={chat}
                            active={activeChatId === chat.id}
                            onClick={() => onChatSelect(chat.id)}
                        />
                    ))}
                </div>

                <Separator className="my-2" style={{ backgroundColor: "var(--surface1)" }} />

                <p
                    className="text-[10px] font-semibold tracking-wider px-2 mb-1 mt-3"
                    style={{ color: "var(--overlay1)" }}
                >
                    DIRECT MESSAGES
                </p>
                <div className="space-y-0.5">
                    {DIRECT_CHATS.map((chat) => (
                        <ChatRow
                            key={chat.id}
                            chat={chat}
                            active={activeChatId === chat.id}
                            onClick={() => onChatSelect(chat.id)}
                        />
                    ))}
                </div>
            </ScrollArea>
        </>
    );
}
