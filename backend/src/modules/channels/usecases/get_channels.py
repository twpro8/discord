from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade


class GetChannelsUseCase:
    def __init__(
        self,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._channels = channel_repository
        self._servers = servers_facade

    async def __call__(self, *, user_id: UUID, server_id: UUID) -> list[Channel]:
        await self._servers.assert_is_server_member(user_id, server_id)
        return await self._channels.list_by_server(server_id)
