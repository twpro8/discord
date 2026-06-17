import { useState, type KeyboardEvent } from "react";
import { Input } from "@/components/ui/input";
import { Paperclip, Smile, Send } from "lucide-react";

interface MessageInputProps {
    placeholder?: string;
    onSend: (text: string) => void;
    disabled?: boolean;
}

export function MessageInput({
                                 placeholder = "Type a message...",
                                 onSend,
                                 disabled = false,
                             }: MessageInputProps) {
    const [value, setValue] = useState("");

    function handleSend() {
        const trimmed = value.trim();
        if (!trimmed || disabled) return;
        onSend(trimmed);
        setValue("");
    }

    function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }

    return (
        <div className="px-4 pb-4 pt-2 shrink-0">
            <div
                className="flex items-center gap-2 rounded-lg px-3 py-2"
                style={{
                    backgroundColor: "var(--surface0)",
                    border: "1px solid var(--surface1)",
                }}
            >
                <button
                    className="shrink-0 hover:opacity-80 transition-opacity"
                    style={{ color: "var(--overlay1)" }}
                    aria-label="Attach file"
                >
                    <Paperclip size={16} />
                </button>

                <Input
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    disabled={disabled}
                    className="flex-1 border-0 bg-transparent p-0 h-auto focus-visible:ring-0 text-sm placeholder:text-(--overlay1)"
                    style={{ color: "var(--text)" }}
                />

                <button
                    className="shrink-0 hover:opacity-80 transition-opacity"
                    style={{ color: "var(--overlay1)" }}
                    aria-label="Add emoji"
                >
                    <Smile size={16} />
                </button>

                <button
                    onClick={handleSend}
                    disabled={disabled || !value.trim()}
                    className="shrink-0 hover:opacity-90 transition-opacity disabled:opacity-40"
                    style={{ color: value.trim() ? "var(--mauve)" : "var(--overlay1)" }}
                    aria-label="Send message"
                >
                    <Send size={16} />
                </button>
            </div>
        </div>
    );
}
