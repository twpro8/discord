from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.exceptions import ChannelConflictError
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.servers.public.facade import ServersFacade


class CreateChannelUseCase:
    def __init__(
        self,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade | None = None,
    ) -> None:
        self._channels = channel_repository
        self._servers = servers_facade

    async def __call__(
        self,
        *,
        server_id: UUID,
        name: str,
        user_id: UUID | None = None,
        channel_type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
    ) -> Channel:
        if self._servers is not None:
            if user_id is None:
                raise ValueError("user_id is required when servers_facade is provided")
            await self._servers.assert_is_server_owner(user_id, server_id)
        name = name.strip()
        existing = await self._channels.find_by_name(server_id, name)
        if existing is not None:
            raise ChannelConflictError
        max_pos = await self._channels.max_position_by_server(server_id)
        channel_data = ChannelCreate(
            server_id=server_id,
            name=name,
            type=channel_type,
            position=max_pos + 1,
            topic=topic,
            is_private=is_private,
        )
        return await self._channels.create(channel_data)
