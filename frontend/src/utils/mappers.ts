import type { ChatSummary, ChatEntry } from "@/types/chat";
import { colorFromId, getInitials, formatRelativeTime } from "@/utils";

export function toChatEntry(chat: ChatSummary): ChatEntry {
    const isGroup = chat.type === "group";
    const name = isGroup ? chat.name : chat.peer_name;
    const avatarUrl = isGroup ? chat.image_url : chat.peer_avatar_url;

    return {
        id: chat.id,
        isGroup,
        name,
        avatarUrl,
        initials: getInitials(name),
        color: colorFromId(chat.id),
        time: chat.last_message ? formatRelativeTime(chat.last_message.created_at) : "",
        lastMessage: chat.last_message?.body ?? "No messages yet",
        unread: chat.unread_count,
    };
}
