from uuid import UUID

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.messages.domain.cursor import decode_cursor
from src.modules.messages.domain.entities.dtos import ChannelMessagePage
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.modules.servers.public.facade import ServersFacade


class ListChannelMessagesUseCase:
    def __init__(
        self,
        message_repository: MessageRepository,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._messages = message_repository
        self._channels = channel_repository
        self._servers_facade = servers_facade

    async def __call__(
        self,
        *,
        channel_id: UUID,
        user_id: UUID,
        limit: int,
        before_cursor: str | None = None,
        after_cursor: str | None = None,
    ) -> ChannelMessagePage:
        channel = await self._channels.find_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_member(user_id, channel.server_id)

        before = decode_cursor(before_cursor) if before_cursor else None
        after = decode_cursor(after_cursor) if after_cursor else None

        return await self._messages.list_for_channel(channel_id, limit, before, after)
