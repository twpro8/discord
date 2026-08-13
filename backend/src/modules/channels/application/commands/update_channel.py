from dataclasses import dataclass
from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelUpdate, ChannelUpdateData
from src.modules.channels.domain.exceptions import (
    ChannelConflictError,
    ChannelNotFoundError,
)
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.command import Command
from src.shared.domain.unset import UNSET
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class UpdateChannelCommand(Command):
    channel_id: UUID
    user_id: UUID
    server_id: UUID
    update_data: ChannelUpdateData


class UpdateChannelCommandHandler:
    def __init__(self, uow: ChannelUnitOfWork, servers_facade: ServersFacade) -> None:
        self._uow = uow
        self._servers_facade = servers_facade

    async def handle(
        self, command: UpdateChannelCommand
    ) -> Result[Channel, LumiereError]:
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

        update_data = command.update_data
        name = update_data.name
        if name is not UNSET and name != channel.name:
            assert isinstance(name, str)
            if (
                await self._uow.channels.find_by_name(channel.server_id, name)
                is not None
            ):
                return Result.err(ChannelConflictError())

        topic = update_data.topic
        if topic is not UNSET and topic == "":
            topic = None

        updated = await self._uow.channels.update(
            channel.id,
            ChannelUpdate(
                name=update_data.name,
                topic=topic,
                position=update_data.position,
            ),
        )

        await self._uow.commit()
        return Result.ok(updated)
