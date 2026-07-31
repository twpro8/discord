from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class MarkChatAsReadCommand(Command):
    chat_id: UUID
    user_id: UUID
    up_to_sequence: int | None = None


class MarkChatAsReadCommandHandler:
    def __init__(self, uow: ChatUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: MarkChatAsReadCommand
    ) -> Result[None, LumiereError]:
        try:
            chat = await services.assert_is_chat_member(
                self._uow.chats, self._uow.members, command.user_id, command.chat_id
            )
        except LumiereError as error:
            return Result.err(error)

        target = (
            command.up_to_sequence
            if command.up_to_sequence is not None
            else chat.last_sequence
        )
        await self._uow.members.update_last_read_seq(
            command.chat_id, command.user_id, target
        )
        await self._uow.commit()
        return Result.ok(None)
