from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import ChatMemberSummary
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class ListMembersQuery(Query):
    chat_id: UUID
    user_id: UUID


class ListMembersQueryHandler:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._chat_members = chat_member_repository

    async def handle(
        self, query: ListMembersQuery
    ) -> Result[list[ChatMemberSummary], LumiereError]:
        try:
            await services.assert_is_chat_member(
                self._chats, self._chat_members, query.user_id, query.chat_id
            )
        except LumiereError as error:
            return Result.err(error)

        members = await self._chat_members.list_active_with_user(query.chat_id)
        return Result.ok(members)
