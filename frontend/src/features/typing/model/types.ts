/** Aligned with the backend's typing.update WS event payload. */
export interface TypingUpdate {
  chat_id: string;
  user_id: string;
  is_typing: boolean;
}
