from uuid import UUID

from src.modules.channels.domain.exceptions import (
    ChannelNotFoundError,
    OnlyChannelDeletionError,
)
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade


class DeleteChannelUseCase:
    def __init__(self, uow: ChannelUnitOfWork, servers_facade: ServersFacade) -> None:
        self._uow = uow
        self._servers_facade = servers_facade

    async def __call__(
        self, *, channel_id: UUID, user_id: UUID, server_id: UUID
    ) -> None:
        channel = await self._uow.channels.find_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError
        if channel.server_id != server_id:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_owner(user_id, channel.server_id)

        if await self._uow.channels.count_by_server(channel.server_id) <= 1:
            raise OnlyChannelDeletionError

        await self._uow.channels.delete(channel.id)
        await self._uow.commit()
