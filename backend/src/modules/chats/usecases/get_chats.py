from uuid import UUID

from src.modules.chats.domain.entities.dtos import ChatSummaryPage
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


class GetChatsUseCase:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self._chats = chat_repository

    async def __call__(
        self, *, user_id: UUID, limit: int, cursor: str | None
    ) -> ChatSummaryPage:
        return await self._chats.list_chats_for_user(user_id, limit, cursor)
