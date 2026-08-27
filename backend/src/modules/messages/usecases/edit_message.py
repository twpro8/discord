from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.modules.messages.domain.entities.dtos import MessageEditData
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.domain.exceptions import (
    MessageEditWindowExpiredError,
    MessageNotFoundError,
    NotMessageSenderError,
)
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)

EDIT_WINDOW = timedelta(hours=24)


class EditMessageUseCase:
    def __init__(self, message_repository: MessageRepository) -> None:
        self._messages = message_repository

    async def __call__(
        self,
        *,
        message_id: UUID,
        sender_id: UUID,
        data: MessageEditData,
        chat_id: UUID | None = None,
        channel_id: UUID | None = None,
    ) -> Message:
        message = await self._messages.find_by_id(message_id)
        if message is None:
            raise MessageNotFoundError

        if (chat_id is not None and message.chat_id != chat_id) or (
            channel_id is not None and message.channel_id != channel_id
        ):
            raise MessageNotFoundError

        if message.sender_id != sender_id:
            raise NotMessageSenderError

        if datetime.now(UTC) - message.created_at > EDIT_WINDOW:
            raise MessageEditWindowExpiredError

        return await self._messages.update_body(message_id, data.body)
