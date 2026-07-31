from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.cursor import decode_cursor
from src.modules.messages.domain.entities.dtos import ChatMessagePage
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class ListChatMessagesQuery(Query):
    chat_id: UUID
    user_id: UUID
    limit: int
    before_cursor: str | None = None
    after_cursor: str | None = None


class ListChatMessagesQueryHandler:
    def __init__(
        self,
        message_repository: MessageRepository,
        chats_facade: ChatsFacade,
    ) -> None:
        self._messages = message_repository
        self._chats_facade = chats_facade

    async def handle(
        self, query: ListChatMessagesQuery
    ) -> Result[ChatMessagePage, LumiereError]:
        try:
            await self._chats_facade.assert_is_chat_member(query.user_id, query.chat_id)
        except LumiereError as error:
            return Result.err(error)

        before = decode_cursor(query.before_cursor) if query.before_cursor else None
        after = decode_cursor(query.after_cursor) if query.after_cursor else None

        page = await self._messages.list_for_chat(
            query.chat_id, query.limit, before, after
        )
        return Result.ok(page)
