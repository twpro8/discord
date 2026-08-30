from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate, ChannelUpdate
from src.shared.domain.unset import set_fields


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

    async def get_by_id(self, channel_id: UUID) -> Channel | None:
        return self.channels.get(channel_id)

    async def find_by_name(self, server_id: UUID, name: str) -> Channel | None:
        return next(
            (
                channel
                for channel in self.channels.values()
                if channel.server_id == server_id and channel.name == name
            ),
            None,
        )

    async def update(self, channel_id: UUID, data: ChannelUpdate) -> Channel:
        channel = self.channels[channel_id]
        for key, value in set_fields(data).items():
            setattr(channel, key, value)
        channel.updated_at = datetime.now(UTC)
        return channel

    async def delete(self, channel_id: UUID) -> None:
        self.channels.pop(channel_id, None)

    async def count_by_server(self, server_id: UUID) -> int:
        return sum(
            1 for channel in self.channels.values() if channel.server_id == server_id
        )

    async def increment_sequence(self, channel_id: UUID) -> int:
        channel = self.channels[channel_id]
        channel.last_sequence += 1
        return channel.last_sequence
