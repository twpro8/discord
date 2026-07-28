from typing import Protocol
from uuid import UUID

from src.modules.chats.domain.entities.chat import ChatMember
from src.modules.chats.domain.entities.schemas import MemberCreate


class ChatMemberRepository(Protocol):
    async def add_members(self, members: list[MemberCreate]) -> None: ...

    async def find_active(self, chat_id: UUID, user_id: UUID) -> ChatMember | None: ...
