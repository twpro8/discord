from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain.entities.dtos import ChatSummary
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetChatDetailsQuery(Query):
    chat_id: UUID
    user_id: UUID


class GetChatDetailsQueryHandler:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._chat_members = chat_member_repository

    async def handle(
        self, query: GetChatDetailsQuery
    ) -> Result[ChatSummary, LumiereError]:
        chat = await self._chats.find_by_id(query.chat_id)
        if chat is None:
            return Result.err(ChatNotFoundError())

        membership = await self._chat_members.find_active(query.chat_id, query.user_id)
        if membership is None:
            return Result.err(NotChatMemberError())

        summary = await self._chats.get_summary_for_user(query.chat_id, query.user_id)
        assert summary is not None
        return Result.ok(summary)
