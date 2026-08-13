from dataclasses import dataclass
from uuid import UUID

from src.modules.channels.domain.exceptions import (
    ChannelNotFoundError,
    OnlyChannelDeletionError,
)
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class DeleteChannelCommand(Command):
    channel_id: UUID
    user_id: UUID
    server_id: UUID


class DeleteChannelCommandHandler:
    def __init__(self, uow: ChannelUnitOfWork, servers_facade: ServersFacade) -> None:
        self._uow = uow
        self._servers_facade = servers_facade

    async def handle(self, command: DeleteChannelCommand) -> Result[None, LumiereError]:
        channel = await self._uow.channels.find_by_id(command.channel_id)
        if channel is None:
            return Result.err(ChannelNotFoundError())
        if channel.server_id != command.server_id:
            return Result.err(ChannelNotFoundError())

        try:
            await self._servers_facade.assert_is_server_owner(
                command.user_id, channel.server_id
            )
        except LumiereError as error:
            return Result.err(error)

        if await self._uow.channels.count_by_server(channel.server_id) <= 1:
            return Result.err(OnlyChannelDeletionError())

        await self._uow.channels.delete(channel.id)
        await self._uow.commit()
        return Result.ok(None)
