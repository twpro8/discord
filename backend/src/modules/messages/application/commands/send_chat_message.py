from uuid import UUID

from src.modules.messages.domain.entities.schemas import (
    ChatMessage,
    MessageCreate,
    MessageCreateRequest,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.shared.errors import LumiereError
from src.shared.permissions import assert_is_chat_member
from src.shared.result import Result


class SendChatMessageCommand:
    def __init__(self, uow: MessageUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, chat_id: UUID, sender_id: UUID, data: MessageCreateRequest
    ) -> Result[ChatMessage, LumiereError]:
        try:
            await assert_is_chat_member(self._uow, sender_id, chat_id)
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
