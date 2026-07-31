from typing import Protocol
from uuid import UUID

from src.modules.messages.domain.entities.dtos import (
    ChannelMessagePage,
    ChatMessagePage,
    MessageCreate,
)
from src.modules.messages.domain.entities.message import Message


class MessageRepository(Protocol):
    async def create(self, data: MessageCreate) -> Message: ...

    async def find_by_id(self, message_id: UUID) -> Message | None: ...

    async def list_for_chat(
        self,
        chat_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChatMessagePage: ...

    async def list_for_channel(
        self,
        channel_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChannelMessagePage: ...

    async def update_body(self, message_id: UUID, body: str) -> Message: ...

    async def soft_delete(self, message_id: UUID) -> Message: ...
