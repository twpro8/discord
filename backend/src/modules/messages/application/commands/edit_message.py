from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.modules.messages.domain.entities.dtos import MessageEditData
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.domain.exceptions import (
    MessageEditWindowExpiredError,
    MessageNotFoundError,
    NotMessageSenderError,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result

EDIT_WINDOW = timedelta(hours=24)


@dataclass(frozen=True, kw_only=True)
class EditMessageCommand(Command):
    message_id: UUID
    sender_id: UUID
    data: MessageEditData
    chat_id: UUID | None = None
    channel_id: UUID | None = None


class EditMessageCommandHandler:
    def __init__(self, uow: MessageUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: EditMessageCommand
    ) -> Result[Message, LumiereError]:
        message = await self._uow.messages.find_by_id(command.message_id)
        if message is None:
            return Result.err(MessageNotFoundError())

        if (command.chat_id is not None and message.chat_id != command.chat_id) or (
            command.channel_id is not None and message.channel_id != command.channel_id
        ):
            return Result.err(MessageNotFoundError())

        if message.sender_id != command.sender_id:
            return Result.err(NotMessageSenderError())

        if datetime.now(UTC) - message.created_at > EDIT_WINDOW:
            return Result.err(MessageEditWindowExpiredError())

        updated = await self._uow.messages.update_body(
            command.message_id, command.data.body
        )
        await self._uow.commit()
        return Result.ok(updated)
