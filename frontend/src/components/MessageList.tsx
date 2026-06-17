import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/Avatar";
import type { Message } from "@/types";

interface MessageListProps {
    messages: Message[];
}

function MessageRow({ msg }: { msg: Message }) {
    return (
        <div
            className="flex gap-3 px-4 py-2 rounded-lg transition-colors"
            onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor = "var(--surface0)")
            }
            onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor = "transparent")
            }
        >
            <Avatar initials={msg.initials} color={msg.color} size="md" />
            <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2 mb-0.5">
          <span
              className="text-sm font-semibold"
              style={{ color: "var(--text)" }}
          >
            {msg.author}
          </span>
                    <span className="text-xs" style={{ color: "var(--overlay1)" }}>
            {msg.time}
          </span>
                </div>

                {msg.quoted ? (
                    <div
                        className="rounded-md px-3 py-1.5 text-sm inline-block"
                        style={{
                            backgroundColor: "var(--surface0)",
                            color: "var(--text)",
                        }}
                    >
                        {msg.text}
                    </div>
                ) : (
                    <p className="text-sm" style={{ color: "var(--text)" }}>
                        {msg.text}
                    </p>
                )}
            </div>
        </div>
    );
}

export function MessageList({ messages }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <ScrollArea className="flex-1 py-4">
            <div className="space-y-1">
                {messages.map((msg) => (
                    <MessageRow key={msg.id} msg={msg} />
                ))}
            </div>
            <div ref={bottomRef} />
        </ScrollArea>
    );
}
