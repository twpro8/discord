from uuid import UUID

from src.modules.chats.domain.entities.schemas import ChatSummaryPage
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.shared.errors import LumiereError
from src.shared.result import Result


class GetChatsQuery:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self._chats = chat_repository

    async def __call__(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> Result[ChatSummaryPage, LumiereError]:
        page = await self._chats.list_chats_for_user(user_id, limit, cursor)
        return Result.ok(page)
