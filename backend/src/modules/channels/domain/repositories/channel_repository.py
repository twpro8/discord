from typing import Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.channels.domain.entities.channel import Channel


class ChannelRepository(Protocol):
    async def create(self, data: BaseModel) -> Channel: ...

    async def get_by_id(self, channel_id: UUID) -> Channel | None: ...

    async def increment_sequence(self, channel_id: UUID) -> int: ...
