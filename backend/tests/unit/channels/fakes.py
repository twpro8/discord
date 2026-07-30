from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)


class FakeChannelRepository:
    def __init__(self) -> None:
        self.channels: dict[UUID, Channel] = {}

    async def create(self, data: ChannelCreate) -> Channel:
        now = datetime.now(UTC)
        channel = Channel(
            id=uuid4(),
            name=data.name,
            server_id=data.server_id,
            type=data.type,
            topic=data.topic,
            position=data.position,
            last_sequence=0,
            is_private=data.is_private,
            created_at=now,
            updated_at=now,
        )
        self.channels[channel.id] = channel
        return channel

    async def find_by_id(self, channel_id: UUID) -> Channel | None:
        return self.channels.get(channel_id)

    async def increment_sequence(self, channel_id: UUID) -> int:
        channel = self.channels[channel_id]
        channel.last_sequence += 1
        return channel.last_sequence


class FakeChannelUnitOfWork(ChannelUnitOfWork):
    def __init__(self, channels: FakeChannelRepository) -> None:
        self.channels = channels
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
