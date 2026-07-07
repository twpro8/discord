from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound

from src.channel.exceptions import ChannelNotFoundError
from src.channel.mappers import ChannelMapper
from src.channel.models import ChannelOrm
from src.channel.schemas import ChannelSchema
from src.core.repositories import BaseRepository


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
        try:
            last_sequence = (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise ChannelNotFoundError
        return last_sequence
