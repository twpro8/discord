from datetime import datetime
from uuid import UUID

from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class Chat(AggregateRoot):
    def __init__(
        self,
        id: UUID,
        type: ChatType,
        name: str | None,
        description: str | None,
        owner_id: UUID | None,
        image_url: str | None,
        last_sequence: int,
        is_archived: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.type = type
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.image_url = image_url
        self.last_sequence = last_sequence
        self.is_archived = is_archived
        self.created_at = created_at
        self.updated_at = updated_at


class ChatMember(Entity):
    def __init__(
        self,
        id: UUID,
        chat_id: UUID,
        user_id: UUID,
        role: ChatMemberRole,
        last_read_seq: int,
        joined_at: datetime,
        left_at: datetime | None,
    ) -> None:
        super().__init__(id)
        self.chat_id = chat_id
        self.user_id = user_id
        self.role = role
        self.last_read_seq = last_read_seq
        self.joined_at = joined_at
        self.left_at = left_at
