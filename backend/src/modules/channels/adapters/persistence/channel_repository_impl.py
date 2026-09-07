from uuid import UUID

from sqlalchemy import func, select, update

from src.modules.channels.adapters.persistence.mappers import ChannelDataMapper
from src.modules.channels.adapters.persistence.models import ChannelOrm
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate, ChannelUpdate
from src.shared.adapters.base_repository import BaseRepository


class ChannelRepositoryImpl(
    BaseRepository[ChannelOrm, Channel, ChannelCreate, ChannelUpdate]
):
    _model = ChannelOrm
    _mapper = ChannelDataMapper

    async def find_by_name(self, server_id: UUID, name: str) -> Channel | None:
        query = select(ChannelOrm).where(
            ChannelOrm.server_id == server_id, ChannelOrm.name == name
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChannelDataMapper.to_entity(model) if model else None

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

    async def list_by_server(self, server_id: UUID) -> list[Channel]:
        query = (
            select(ChannelOrm)
            .where(ChannelOrm.server_id == server_id)
            .order_by(ChannelOrm.position.asc())
        )
        return await self._execute_and_map_all(query)
