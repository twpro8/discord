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
from src.shared.permissions import assert_is_server_member


class SendChannelMessageCommand:
    def __init__(self, uow: MessageUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        channel_id: UUID,
        sender_id: UUID,
        data: MessageCreateRequest,
    ) -> ChannelMessage:
        channel = await self._uow.channels.find_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError

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
        await self._uow.commit()
        return ChannelMessage.model_validate(message)
