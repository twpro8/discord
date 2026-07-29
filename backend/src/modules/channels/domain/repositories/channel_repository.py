from typing import Protocol
from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.schemas import ChannelCreate


class ChannelRepository(Protocol):
    async def create(self, data: ChannelCreate) -> Channel: ...

    async def find_by_id(self, channel_id: UUID) -> Channel | None: ...

    async def increment_sequence(self, channel_id: UUID) -> int: ...
