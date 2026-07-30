from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.entities.schemas import (
    ChatMessage,
    MessageCreate,
    MessageCreateRequest,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class SendChatMessageCommand(Command):
    chat_id: UUID
    sender_id: UUID
    data: MessageCreateRequest


class SendChatMessageCommandHandler:
    def __init__(self, uow: MessageUnitOfWork, chats_facade: ChatsFacade) -> None:
        self._uow = uow
        self._chats_facade = chats_facade

    async def handle(
        self, command: SendChatMessageCommand
    ) -> Result[ChatMessage, LumiereError]:
        chat_id, sender_id, data = command.chat_id, command.sender_id, command.data
        try:
            await self._chats_facade.assert_is_chat_member(sender_id, chat_id)
            sequence = await self._uow.chats.increment_sequence(chat_id)
            message = await self._uow.messages.create(
                MessageCreate(
                    chat_id=chat_id,
                    sender_id=sender_id,
                    sequence=sequence,
                    **data.model_dump(),
                )
            )
        except LumiereError as error:
            return Result.err(error)

        await self._uow.commit()
        return Result.ok(ChatMessage.model_validate(message))
