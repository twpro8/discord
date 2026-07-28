from datetime import datetime
from uuid import UUID

from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.shared.schemas import BaseSchema


class Chat(BaseSchema):
    id: UUID
    type: ChatType
    name: str | None
    description: str | None
    owner_id: UUID | None
    image_url: str | None
    last_sequence: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class ChatMember(BaseSchema):
    id: UUID
    chat_id: UUID
    user_id: UUID
    role: ChatMemberRole
    last_read_seq: int
    joined_at: datetime
    left_at: datetime | None
