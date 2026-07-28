from typing import Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.chats.domain.entities.chat import Chat, ChatMember
from src.modules.chats.domain.entities.schemas import ChatSummaryPage, MemberCreate


class ChatRepository(Protocol):
    async def create(self, data: BaseModel) -> Chat: ...

    async def get_by_id(self, chat_id: UUID) -> Chat | None: ...

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> Chat | None: ...

    async def increment_sequence(self, chat_id: UUID) -> int: ...

    async def list_chats_for_user(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage: ...


class ChatMemberRepository(Protocol):
    async def add_members(self, members: list[MemberCreate]) -> None: ...

    async def get_active(self, chat_id: UUID, user_id: UUID) -> ChatMember | None: ...
