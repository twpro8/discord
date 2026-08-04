from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chats.domain import services
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)


class ChatsFacade(Protocol):
    """The only way other modules may check chat membership/ownership.
    Raises chats' own domain exceptions (ChatNotFoundError,
    NotChatMemberError, NotChatOwnerError) — callers catch LumiereError at
    their own command boundary and convert to a Result, matching this
    codebase's established cross-module delegation convention."""

    async def assert_is_chat_member(self, user_id: UUID, chat_id: UUID) -> None: ...

    async def assert_is_chat_owner(self, user_id: UUID, chat_id: UUID) -> None: ...

    async def list_active_user_ids(self, chat_id: UUID) -> set[UUID]: ...


class RepositoryBackedChatsFacade:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._chat_members = chat_member_repository

    async def assert_is_chat_member(self, user_id: UUID, chat_id: UUID) -> None:
        await services.assert_is_chat_member(
            self._chats, self._chat_members, user_id, chat_id
        )

    async def assert_is_chat_owner(self, user_id: UUID, chat_id: UUID) -> None:
        await services.assert_is_chat_owner(
            self._chats, self._chat_members, user_id, chat_id
        )

    async def list_active_user_ids(self, chat_id: UUID) -> set[UUID]:
        return await self._chat_members.list_active_user_ids(chat_id)


def build_chats_facade(session: AsyncSession) -> ChatsFacade:
    return RepositoryBackedChatsFacade(
        ChatRepositoryImpl(session), ChatMemberRepositoryImpl(session)
    )
