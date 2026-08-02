/** Chat message shape, aligned with the backend ChatMessageResponse schema. */
export interface ChatMessage {
  id: string;
  sender_id: string;
  body: string | null;
  sequence: number;
  parent_id: string | null;
  is_edited: boolean;
  is_deleted: boolean;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
  chat_id: string;
}

/** Paginated chat message response, aligned with ChatMessagePageResponse. */
export interface ChatMessagePage {
  items: ChatMessage[];
  next_cursor: string | null;
  has_more: boolean;
}

/** Private chat summary, aligned with PrivateChatSummaryResponse. */
export interface PrivateChatSummary {
  id: string;
  type: "private";
  peer_id: string;
  peer_name: string;
  peer_avatar_url: string | null;
  unread_count: number;
  last_message: {
    sender_id: string;
    body: string | null;
    created_at: string;
  } | null;
}
