from uuid import UUID

from sqlalchemy import update

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.infrastructure.persistence.mappers import ChannelMapper
from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.shared.repositories import BaseRepository


class ChannelRepository(BaseRepository[ChannelOrm, Channel]):
    model = ChannelOrm
    schema = Channel
    mapper = ChannelMapper

    async def increment_sequence(self, channel_id: UUID) -> int:
        stmt = (
            update(ChannelOrm)
            .where(ChannelOrm.id == channel_id)
            .values(last_sequence=ChannelOrm.last_sequence + 1)
            .returning(ChannelOrm.last_sequence)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
