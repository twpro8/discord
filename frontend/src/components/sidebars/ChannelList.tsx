import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Hash, Volume2, ChevronDown } from "lucide-react";
import { TEXT_CHANNELS, VOICE_CHANNELS } from "@/data";
import type { TextChannel, VoiceChannel } from "@/types";

interface ChannelListProps {
    activeChannelId: string | null;
    onChannelSelect: (id: string) => void;
}

function TextChannelRow({ channel, active, onClick }: {
    channel: TextChannel;
    active: boolean;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className="w-full flex items-center gap-1.5 px-2 py-1 rounded-md text-sm transition-colors"
            style={{
                backgroundColor: active ? "var(--surface1)" : "transparent",
                color: active
                    ? "var(--text)"
                    : channel.unread
                        ? "var(--subtext1)"
                        : "var(--overlay1)",
                fontWeight: channel.unread && !active ? 600 : 400,
            }}
        >
            <Hash size={14} className="shrink-0" />
            <span className="truncate">{channel.name}</span>
            {channel.unread && !active && (
                <div
                    className="ml-auto w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: "var(--mauve)" }}
                />
            )}
        </button>
    );
}

function VoiceChannelRow({ channel }: { channel: VoiceChannel }) {
    return (
        <button
            className="w-full flex items-center gap-1.5 px-2 py-1 rounded-md text-sm transition-colors hover:bg-(--surface0)"
            style={{ color: channel.active ? "var(--green)" : "var(--overlay1)" }}
        >
            <Volume2 size={14} className="shrink-0" />
            <span className="truncate">{channel.name}</span>
            {channel.active && (
                <Badge
                    variant="secondary"
                    className="ml-auto text-[9px] px-1 py-0 h-4"
                    style={{
                        backgroundColor: "var(--surface1)",
                        color: "var(--green)",
                    }}
                >
                    LIVE
                </Badge>
            )}
        </button>
    );
}

export function ChannelList({ activeChannelId, onChannelSelect }: ChannelListProps) {
    return (
        <>
            {/* Workspace header */}
            <button
                className="flex items-center justify-between px-4 py-3 font-semibold hover:bg-(--surface0) transition-colors w-full shrink-0"
                style={{
                    color: "var(--text)",
                    borderBottom: "1px solid var(--surface1)",
                }}
            >
                <span className="text-sm">Lumiere HQ</span>
                <ChevronDown size={14} style={{ color: "var(--overlay1)" }} />
            </button>

            <ScrollArea className="flex-1 py-2">
                {/* Text channels */}
                <div className="px-2 mb-1">
                    <p
                        className="text-[10px] font-semibold tracking-wider px-2 mb-1"
                        style={{ color: "var(--overlay1)" }}
                    >
                        CHANNELS
                    </p>
                    {TEXT_CHANNELS.map((ch) => (
                        <TextChannelRow
                            key={ch.id}
                            channel={ch}
                            active={ch.id === activeChannelId}
                            onClick={() => onChannelSelect(ch.id)}
                        />
                    ))}
                </div>

                <Separator className="my-2 mx-2" style={{ backgroundColor: "var(--surface1)" }} />

                {/* Voice channels */}
                <div className="px-2">
                    <p
                        className="text-[10px] font-semibold tracking-wider px-2 mb-1"
                        style={{ color: "var(--overlay1)" }}
                    >
                        VOICE
                    </p>
                    {VOICE_CHANNELS.map((ch) => (
                        <VoiceChannelRow key={ch.id} channel={ch} />
                    ))}
                </div>
            </ScrollArea>
        </>
    );
}
