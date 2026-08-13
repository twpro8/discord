from dataclasses import asdict
from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate, ChannelUpdate
from src.modules.channels.infrastructure.persistence.mappers import ChannelDataMapper
from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.shared.domain.unset import set_fields


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

    async def find_by_name(self, server_id: UUID, name: str) -> Channel | None:
        query = select(ChannelOrm).where(
            ChannelOrm.server_id == server_id, ChannelOrm.name == name
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChannelDataMapper.to_entity(model) if model else None

    async def update(self, channel_id: UUID, data: ChannelUpdate) -> Channel:
        stmt = (
            update(ChannelOrm)
            .where(ChannelOrm.id == channel_id)
            .values(updated_at=func.now(), **set_fields(data))
            .returning(ChannelOrm)
        )
        result = await self._session.execute(stmt)
        return ChannelDataMapper.to_entity(result.scalar_one())

    async def delete(self, channel_id: UUID) -> None:
        stmt = delete(ChannelOrm).where(ChannelOrm.id == channel_id)
        await self._session.execute(stmt)

    async def count_by_server(self, server_id: UUID) -> int:
        stmt = select(func.count(ChannelOrm.id)).where(
            ChannelOrm.server_id == server_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def increment_sequence(self, channel_id: UUID) -> int:
        stmt = (
            update(ChannelOrm)
            .where(ChannelOrm.id == channel_id)
            .values(last_sequence=ChannelOrm.last_sequence + 1)
            .returning(ChannelOrm.last_sequence)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
