from uuid import UUID

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.messages.domain.entities.dtos import (
    ChannelMessage,
    MessageCreate,
    MessageCreateData,
    channel_message_from_message,
)
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.modules.servers.public.facade import ServersFacade


class SendChannelMessageUseCase:
    def __init__(
        self,
        message_repository: MessageRepository,
        channel_repository: ChannelRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._messages = message_repository
        self._channels = channel_repository
        self._servers_facade = servers_facade

    async def __call__(
        self, *, channel_id: UUID, sender_id: UUID, data: MessageCreateData
    ) -> ChannelMessage:
        channel = await self._channels.get_by_id(channel_id)
        if channel is None:
            raise ChannelNotFoundError

        await self._servers_facade.assert_is_server_member(sender_id, channel.server_id)
        sequence = await self._channels.increment_sequence(channel_id)
        message = await self._messages.create(
            MessageCreate(
                channel_id=channel_id,
                sender_id=sender_id,
                sequence=sequence,
                body=data.body,
                parent_id=data.parent_id,
            )
        )

        return channel_message_from_message(message)
