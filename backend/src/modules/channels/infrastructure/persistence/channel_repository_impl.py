from dataclasses import asdict
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.infrastructure.persistence.mappers import ChannelDataMapper
from src.modules.channels.infrastructure.persistence.models import ChannelOrm


class ChannelRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ChannelCreate) -> Channel:
        stmt = insert(ChannelOrm).values(**asdict(data)).returning(ChannelOrm)
        result = await self._session.execute(stmt)
        return ChannelDataMapper.to_entity(result.scalar_one())

    async def find_by_id(self, channel_id: UUID) -> Channel | None:
        query = select(ChannelOrm).filter_by(id=channel_id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChannelDataMapper.to_entity(model) if model else None

    async def increment_sequence(self, channel_id: UUID) -> int:
        stmt = (
            update(ChannelOrm)
            .where(ChannelOrm.id == channel_id)
            .values(last_sequence=ChannelOrm.last_sequence + 1)
            .returning(ChannelOrm.last_sequence)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
