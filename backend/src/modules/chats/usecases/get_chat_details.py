from uuid import UUID

from src.modules.chats.domain.entities.dtos import ChatSummary
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


class GetChatDetailsUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._chat_members = chat_member_repository

    async def __call__(self, *, chat_id: UUID, user_id: UUID) -> ChatSummary:
        chat = await self._chats.find_by_id(chat_id)
        if chat is None:
            raise ChatNotFoundError

        membership = await self._chat_members.find_active(chat_id, user_id)
        if membership is None:
            raise NotChatMemberError

        summary = await self._chats.get_summary_for_user(chat_id, user_id)
        assert summary is not None
        return summary
