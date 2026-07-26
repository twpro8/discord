from uuid import UUID

from sqlalchemy import update

from src.kernel.repositories import BaseRepository
from src.modules.channels.mappers import ChannelMapper
from src.modules.channels.models import ChannelOrm
from src.modules.channels.schemas import ChannelSchema


class ChannelRepository(BaseRepository[ChannelOrm, ChannelSchema]):
    model = ChannelOrm
    schema = ChannelSchema
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
