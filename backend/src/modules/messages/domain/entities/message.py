from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class Message(Entity):
    def __init__(
        self,
        id: UUID,
        sender_id: UUID,
        body: str | None,
        sequence: int,
        parent_id: UUID | None,
        is_edited: bool,
        is_deleted: bool,
        deleted_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
        chat_id: UUID | None,
        channel_id: UUID | None,
    ) -> None:
        super().__init__(id)
        self.sender_id = sender_id
        self.body = body
        self.sequence = sequence
        self.parent_id = parent_id
        self.is_edited = is_edited
        self.is_deleted = is_deleted
        self.deleted_at = deleted_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.chat_id = chat_id
        self.channel_id = channel_id
