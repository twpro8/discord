import { useState, useEffect, useCallback } from "react";
import { Phone, Video, Pin, Bell, Search, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/Avatar";
import { MessageList } from "@/components/MessageList";
import { MessageInput } from "@/components/MessageInput";
import { ChatList } from "@/components/sidebars/ChatList.tsx";
import { useLayout } from "@/context/LayoutContext";
import { GROUP_CHATS, DIRECT_CHATS, DM_MESSAGES } from "@/data";
import type { Message } from "@/types";

const ALL_CHATS = [...GROUP_CHATS, ...DIRECT_CHATS];

function EmptyState() {
    return (
        <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <div
                className="w-16 h-16 rounded-full flex items-center justify-center"
                style={{ backgroundColor: "var(--surface0)" }}
            >
                <Users size={28} style={{ color: "var(--overlay1)" }} />
            </div>
            <p className="text-sm font-medium" style={{ color: "var(--subtext1)" }}>
                Select a chat to start messaging
            </p>
            <p className="text-xs" style={{ color: "var(--overlay1)" }}>
                Choose from your direct messages or group chats
            </p>
        </div>
    );
}

export default function ChatPage() {
    const { setLeftSidebar, setRightSidebar } = useLayout();

    const [activeChatId, setActiveChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Record<string, Message[]>>(DM_MESSAGES);

    const activeChat = ALL_CHATS.find((c) => c.id === activeChatId) ?? null;
    const activeMessages = activeChatId ? (messages[activeChatId] ?? []) : [];

    // Inject DmList into left sidebar
    useEffect(() => {
        setLeftSidebar(
            <ChatList
                activeChatId={activeChatId}
                onChatSelect={setActiveChatId}
            />
        );
        // DM page has no right sidebar
        setRightSidebar(null);
    }, [activeChatId, setLeftSidebar, setRightSidebar]);

    const handleSend = useCallback(
        (text: string) => {
            if (!activeChatId) return;
            setMessages((prev) => ({
                ...prev,
                [activeChatId]: [
                    ...(prev[activeChatId] ?? []),
                    {
                        id: Date.now(),
                        author: "You",
                        initials: "YO",
                        color: "var(--peach)",
                        time: new Date().toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                        }),
                        text,
                    },
                ],
            }));
        },
        [activeChatId]
    );

    if (!activeChat) {
        return <EmptyState />;
    }

    return (
        <>
            {/* Top bar */}
            <div
                className="flex items-center gap-3 px-4 h-12 shrink-0"
                style={{ borderBottom: "1px solid var(--surface1)" }}
            >
                <Avatar
                    initials={activeChat.initials}
                    color={activeChat.color}
                    size="sm"
                    status={!activeChat.isGroup ? activeChat.status : undefined}
                />
                <span
                    className="font-semibold text-sm"
                    style={{ color: "var(--text)" }}
                >
          {activeChat.name}
        </span>

                {!activeChat.isGroup && (
                    <span className="text-xs" style={{ color: "var(--overlay1)" }}>
            {activeChat.status === "online"
                ? "● Online"
                : activeChat.status === "away"
                    ? "○ Away"
                    : "○ Offline"}
          </span>
                )}
                {activeChat.isGroup && (
                    <span className="text-xs" style={{ color: "var(--overlay1)" }}>
            {activeChat.members?.length ?? 0} members
          </span>
                )}

                <div className="flex items-center gap-1 ml-auto">
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-(--surface0)" aria-label="Voice call">
                        <Phone size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-(--surface0)" aria-label="Video call">
                        <Video size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-(--surface0)" aria-label="Pinned messages">
                        <Pin size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-(--surface0)" aria-label="Notifications">
                        <Bell size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <div
                        className="flex items-center gap-1.5 h-8 px-2.5 rounded-md cursor-pointer hover:bg-(--surface0) transition-colors"
                        style={{ border: "1px solid var(--surface1)" }}
                        role="button"
                        aria-label="Search in conversation"
                    >
                        <Search size={13} style={{ color: "var(--overlay1)" }} />
                        <span className="text-xs" style={{ color: "var(--overlay1)" }}>
              Search
            </span>
                    </div>
                </div>
            </div>

            <MessageList messages={activeMessages} />

            <MessageInput
                placeholder={`Message ${activeChat.name}...`}
                onSend={handleSend}
            />
        </>
    );
}
