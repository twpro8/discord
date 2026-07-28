from typing import Protocol
from uuid import UUID

from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.schemas import (
    ChatCreate,
    ChatSummaryPage,
)


class ChatRepository(Protocol):
    async def create(self, data: ChatCreate) -> Chat: ...

    async def find_by_id(self, chat_id: UUID) -> Chat | None: ...

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> Chat | None: ...

    async def increment_sequence(self, chat_id: UUID) -> int: ...

    async def list_chats_for_user(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage: ...
