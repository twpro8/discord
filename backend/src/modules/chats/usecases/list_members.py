from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import ChatMemberSummary
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


class ListMembersUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._chat_members = chat_member_repository

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID
    ) -> list[ChatMemberSummary]:
        await services.assert_is_chat_member(
            self._chats, self._chat_members, user_id, chat_id
        )

        return await self._chat_members.list_active_with_user(chat_id)
