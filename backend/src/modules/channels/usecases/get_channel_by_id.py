from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.exceptions import ChannelNotFoundError
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade


class GetChannelByIDUseCase:
    def __init__(
        self,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._channels = channel_repository
        self._servers = servers_facade

    async def __call__(
        self, *, user_id: UUID, channel_id: UUID, server_id: UUID
    ) -> Channel:
        await self._servers.assert_is_server_member(user_id, server_id)
        channel = await self._channels.get_by_id(channel_id)
        if channel is None or channel.server_id != server_id:
            raise ChannelNotFoundError
        return channel
