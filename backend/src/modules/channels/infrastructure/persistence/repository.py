from uuid import UUID

from sqlalchemy import update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.schemas import ChannelCreate
from src.modules.channels.infrastructure.persistence.mappers import model_to_entity
from src.modules.channels.infrastructure.persistence.models import ChannelOrm


class ChannelRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ChannelCreate) -> Channel:
        stmt = insert(ChannelOrm).values(**data.model_dump()).returning(ChannelOrm)
        result = await self._session.execute(stmt)
        return model_to_entity(result.scalar_one())

    async def increment_sequence(self, channel_id: UUID) -> int:
        stmt = (
            update(ChannelOrm)
            .where(ChannelOrm.id == channel_id)
            .values(last_sequence=ChannelOrm.last_sequence + 1)
            .returning(ChannelOrm.last_sequence)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
