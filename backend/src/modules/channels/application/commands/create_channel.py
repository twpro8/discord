from dataclasses import dataclass
from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class CreateChannelCommand(Command):
    server_id: UUID
    name: str
    type: ChannelType = ChannelType.text
    topic: str | None = None
    is_private: bool = False
    is_commit: bool = True


class CreateChannelCommandHandler:
    def __init__(self, channel_unit_of_work: ChannelUnitOfWork) -> None:
        self._uow = channel_unit_of_work

    async def handle(
        self, command: CreateChannelCommand
    ) -> Result[Channel, LumiereError]:
        channel_data = ChannelCreate(
            server_id=command.server_id,
            name=command.name,
            type=command.type,
            position=0,
            topic=command.topic,
            is_private=command.is_private,
        )

        channel = await self._uow.channels.create(channel_data)
        if command.is_commit:
            await self._uow.commit()

        return Result.ok(channel)
