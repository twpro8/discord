from uuid import UUID

from src.modules.messages.domain.entities.schemas import (
    ChannelMessage,
    MessageCreate,
    MessageCreateRequest,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    AbstractMessageUnitOfWork,
)


class SendChannelMessageCommand:
    def __init__(self, uow: AbstractMessageUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        channel_id: UUID,
        sender_id: UUID,
        data: MessageCreateRequest,
    ) -> ChannelMessage:
        sequence = await self._uow.channels.increment_sequence(channel_id)
        message = await self._uow.messages.create(
            MessageCreate(
                channel_id=channel_id,
                sender_id=sender_id,
                sequence=sequence,
                **data.model_dump(),
            )
        )
        await self._uow.commit()
        return ChannelMessage(**message.model_dump(exclude={"chat_id"}))
