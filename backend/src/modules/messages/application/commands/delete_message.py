from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.domain.exceptions import (
    MessageDeletePermissionError,
    MessageNotFoundError,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class DeleteMessageCommand(Command):
    message_id: UUID
    user_id: UUID
    chat_id: UUID | None = None
    channel_id: UUID | None = None


class DeleteMessageCommandHandler:
    def __init__(
        self,
        uow: MessageUnitOfWork,
        chats_facade: ChatsFacade,
        servers_facade: ServersFacade,
    ) -> None:
        self._uow = uow
        self._chats_facade = chats_facade
        self._servers_facade = servers_facade

    async def handle(
        self, command: DeleteMessageCommand
    ) -> Result[Message, LumiereError]:
        message = await self._uow.messages.find_by_id(command.message_id)
        if message is None:
            return Result.err(MessageNotFoundError())

        if (command.chat_id is not None and message.chat_id != command.chat_id) or (
            command.channel_id is not None and message.channel_id != command.channel_id
        ):
            return Result.err(MessageNotFoundError())

        is_sender = message.sender_id == command.user_id
        is_owner = False

        if not is_sender:
            if message.chat_id is not None:
                try:
                    await self._chats_facade.assert_is_chat_owner(
                        command.user_id, message.chat_id
                    )
                    is_owner = True
                except LumiereError:
                    is_owner = False
            else:
                assert message.channel_id is not None
                channel = await self._uow.channels.find_by_id(message.channel_id)
                if channel is not None:
                    try:
                        await self._servers_facade.assert_is_server_owner(
                            command.user_id, channel.server_id
                        )
                        is_owner = True
                    except LumiereError:
                        is_owner = False

        if not (is_sender or is_owner):
            return Result.err(MessageDeletePermissionError())

        deleted = await self._uow.messages.soft_delete(command.message_id)
        await self._uow.commit()
        return Result.ok(deleted)
