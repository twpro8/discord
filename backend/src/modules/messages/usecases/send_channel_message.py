from uuid import UUID

from src.modules.messages.domain.entities.dtos import (
    ChannelMessage,
    MessageCreate,
    MessageCreateData,
    channel_message_from_message,
)
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade


class SendChannelMessageUseCase:
    def __init__(self, uow: MessageUnitOfWork, servers_facade: ServersFacade) -> None:
        self._uow = uow
        self._servers_facade = servers_facade

    async def __call__(
        self, *, channel_id: UUID, sender_id: UUID, data: MessageCreateData
    ) -> ChannelMessage:
        channel = await self._uow.channels.find_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_member(sender_id, channel.server_id)
        sequence = await self._uow.channels.increment_sequence(channel_id)
        message = await self._uow.messages.create(
            MessageCreate(
                channel_id=channel_id,
                sender_id=sender_id,
                sequence=sequence,
                body=data.body,
                parent_id=data.parent_id,
            )
        )

        await self._uow.commit()
        return channel_message_from_message(message)
