from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain.entities.schemas import ChatSummaryPage
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetChatsQuery(Query):
    user_id: UUID
    limit: int
    cursor: str | None


class GetChatsQueryHandler:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self._chats = chat_repository

    async def handle(
        self, query: GetChatsQuery
    ) -> Result[ChatSummaryPage, LumiereError]:
        page = await self._chats.list_chats_for_user(
            query.user_id, query.limit, query.cursor
        )
        return Result.ok(page)
