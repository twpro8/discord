import type {GroupChatSummary, PrivateChatSummary} from "@/client";

export type ChatSummary = GroupChatSummary | PrivateChatSummary;

export interface ChatEntry {
    id: string;
    isGroup: boolean;
    name: string;
    avatarUrl?: string | null;
    initials: string;
    color: string;
    time: string;
    lastMessage: string;
    unread: number;
    status?: "online" | "offline" | "away";
    members?: string[];
}
