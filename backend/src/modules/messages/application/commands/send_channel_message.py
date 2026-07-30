from dataclasses import dataclass
from uuid import UUID

from src.modules.channels.domain.exceptions import ChannelNotFoundError
from src.modules.messages.domain.entities.schemas import (
    ChannelMessage,
    MessageCreate,
    MessageCreateRequest,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.permissions import assert_is_server_member
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class SendChannelMessageCommand(Command):
    channel_id: UUID
    sender_id: UUID
    data: MessageCreateRequest


class SendChannelMessageCommandHandler:
    def __init__(self, uow: MessageUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: SendChannelMessageCommand
    ) -> Result[ChannelMessage, LumiereError]:
        channel_id, sender_id, data = (
            command.channel_id,
            command.sender_id,
            command.data,
        )
        channel = await self._uow.channels.find_by_id(channel_id)
        if channel is None:
            return Result.err(ChannelNotFoundError())

        try:
            await assert_is_server_member(self._uow, sender_id, channel.server_id)
            sequence = await self._uow.channels.increment_sequence(channel_id)
            message = await self._uow.messages.create(
                MessageCreate(
                    channel_id=channel_id,
                    sender_id=sender_id,
                    sequence=sequence,
                    **data.model_dump(),
                )
            )
        except LumiereError as error:
            return Result.err(error)

        await self._uow.commit()
        return Result.ok(ChannelMessage.model_validate(message))
