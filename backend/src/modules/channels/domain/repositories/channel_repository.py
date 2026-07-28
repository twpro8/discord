from typing import Protocol
from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.messages.domain.entities.schemas import MessageCreate


class ChannelRepository(Protocol):
    async def create(self, data: MessageCreate) -> Channel: ...

    async def increment_sequence(self, channel_id: UUID) -> int: ...
