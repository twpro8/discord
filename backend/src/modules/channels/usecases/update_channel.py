from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelUpdate, ChannelUpdateData
from src.modules.channels.domain.exceptions import (
    ChannelConflictError,
    ChannelNotFoundError,
)
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.domain.unset import UNSET


class UpdateChannelUseCase:
    def __init__(
        self, channel_repository: ChannelRepository, servers_facade: ServersFacade
    ) -> None:
        self._channels = channel_repository
        self._servers_facade = servers_facade

    async def __call__(
        self,
        *,
        channel_id: UUID,
        user_id: UUID,
        server_id: UUID,
        update_data: ChannelUpdateData,
    ) -> Channel:
        channel = await self._channels.find_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError
        if channel.server_id != server_id:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_owner(user_id, channel.server_id)

        name = update_data.name
        if name is not UNSET and name != channel.name:
            assert isinstance(name, str)
            if await self._channels.find_by_name(channel.server_id, name) is not None:
                raise ChannelConflictError

        topic = update_data.topic
        if topic is not UNSET and topic == "":
            topic = None

        return await self._channels.update(
            channel.id,
            ChannelUpdate(
                name=update_data.name,
                topic=topic,
                position=update_data.position,
            ),
        )
