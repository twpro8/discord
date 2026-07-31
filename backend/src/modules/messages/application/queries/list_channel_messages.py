from dataclasses import dataclass
from uuid import UUID

from src.modules.messages.domain.cursor import decode_cursor
from src.modules.messages.domain.entities.dtos import ChannelMessagePage
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class ListChannelMessagesQuery(Query):
    channel_id: UUID
    user_id: UUID
    limit: int
    before_cursor: str | None = None
    after_cursor: str | None = None


class ListChannelMessagesQueryHandler:
    def __init__(
        self,
        uow: MessageUnitOfWork,
        servers_facade: ServersFacade,
    ) -> None:
        self._uow = uow
        self._servers_facade = servers_facade

    async def handle(
        self, query: ListChannelMessagesQuery
    ) -> Result[ChannelMessagePage, LumiereError]:
        channel = await self._uow.channels.find_by_id(query.channel_id)
        if channel is None:
            return Result.err(ChannelNotFoundError())

        try:
            await self._servers_facade.assert_is_server_member(
                query.user_id, channel.server_id
            )
        except LumiereError as error:
            return Result.err(error)

        before = decode_cursor(query.before_cursor) if query.before_cursor else None
        after = decode_cursor(query.after_cursor) if query.after_cursor else None

        page = await self._uow.messages.list_for_channel(
            query.channel_id, query.limit, before, after
        )
        return Result.ok(page)
