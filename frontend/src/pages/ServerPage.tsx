import { useState, useEffect, useCallback } from "react";
import { Hash, Pin, Bell, Search, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { MessageList } from "@/components/MessageList";
import { MessageInput } from "@/components/MessageInput";
import { ChannelList } from "@/components/sidebars/ChannelList";
import { MemberList } from "@/components/sidebars/MemberList";
import { useLayout } from "@/context/LayoutContext";
import { SERVER_MESSAGES } from "@/data";
import type { Message } from "@/types";

function EmptyState() {
    return (
        <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <div
                className="w-16 h-16 rounded-full flex items-center justify-center"
                style={{ backgroundColor: "var(--surface0)" }}
            >
                <Hash size={28} style={{ color: "var(--overlay1)" }} />
            </div>
            <p className="text-sm font-medium" style={{ color: "var(--subtext1)" }}>
                Select a channel to start messaging
            </p>
            <p className="text-xs" style={{ color: "var(--overlay1)" }}>
                Choose from your text channels
            </p>
        </div>
    );
}

export default function ServerPage() {
    const { setLeftSidebar, setRightSidebar, toggleRightSidebar, rightSidebar } =
        useLayout();

    const [activeChannelId, setActiveChannelId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Record<string, Message[]>>(SERVER_MESSAGES);

    // Inject sidebar content when the page mounts / activeChannelId changes
    useEffect(() => {
        setLeftSidebar(
            <ChannelList
                activeChannelId={activeChannelId}
                onChannelSelect={setActiveChannelId}
            />
        );
    }, [activeChannelId, setLeftSidebar]);

    useEffect(() => {
        setRightSidebar(<MemberList />);
        // return () => setRightSidebar(null); // clean up on unmount
    }, [setRightSidebar]);

    const activeMessages = activeChannelId ? (messages[activeChannelId] ?? []) : [];

    const handleSend = useCallback((text: string) => {
        if (!activeChannelId) return;
        setMessages((prev) => ({
            ...prev,
            [activeChannelId]: [
                ...(prev[activeChannelId] ?? []),
                {
                    id: Date.now(),
                    author: "You",
                    initials: "YO",
                    color: "var(--peach)",
                    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                    text,
                },
            ],
        }));
    }, [activeChannelId]);

    if (!activeChannelId) {
        return <EmptyState />;
    }

    return (
        <>
            {/* Top bar */}
            <div
                className="flex items-center gap-3 px-4 h-(--layout-header-height) shrink-0"
                style={{ borderBottom: "1px solid var(--surface1)" }}
            >
                <div
                    className="flex items-center gap-1.5 font-semibold"
                    style={{ color: "var(--text)" }}
                >
                    <Hash size={16} style={{ color: "var(--overlay1)" }} />
                    <span>{activeChannelId}</span>
                </div>

                <Separator
                    orientation="vertical"
                    className="h-5 mx-1"
                    style={{ backgroundColor: "var(--surface2)" }}
                />

                <span className="text-xs" style={{ color: "var(--overlay1)" }}>
          12 members online
        </span>

                <div className="flex items-center gap-1 ml-auto">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 hover:bg-(--surface0)"
                        aria-label="Pinned messages"
                    >
                        <Pin size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 hover:bg-(--surface0)"
                        aria-label="Notifications"
                    >
                        <Bell size={15} style={{ color: "var(--overlay1)" }} />
                    </Button>
                    <div
                        className="flex items-center gap-1.5 h-8 px-2.5 rounded-md cursor-pointer hover:bg-(--surface0) transition-colors"
                        style={{ border: "1px solid var(--surface1)" }}
                        role="button"
                        aria-label="Search"
                    >
                        <Search size={13} style={{ color: "var(--overlay1)" }} />
                        <span className="text-xs" style={{ color: "var(--overlay1)" }}>
              Search
            </span>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 hover:bg-(--surface0)"
                        onClick={toggleRightSidebar}
                        aria-label="Toggle member list"
                        aria-pressed={rightSidebar.visible}
                    >
                        <Users
                            size={15}
                            style={{
                                color: rightSidebar.visible
                                    ? "var(--mauve)"
                                    : "var(--overlay1)",
                            }}
                        />
                    </Button>
                </div>
            </div>

            <MessageList messages={activeMessages} />

            <MessageInput
                placeholder={`Message #${activeChannelId}...`}
                onSend={handleSend}
            />
        </>
    );
}
