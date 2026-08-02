from dataclasses import asdict
from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain.entities.dtos import (
    ServerMemberCreate,
    ServerMemberUpdate,
)
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.infrastructure.persistence.mappers import (
    ServerMemberDataMapper,
)
from src.modules.servers.infrastructure.persistence.models import ServerMemberOrm
from src.shared.domain.unset import set_fields
from src.shared.errors import NotFoundError


class ServerMemberRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ServerMemberCreate) -> ServerMember:
        stmt = insert(ServerMemberOrm).values(**asdict(data)).returning(ServerMemberOrm)
        result = await self._session.execute(stmt)
        return ServerMemberDataMapper.to_entity(result.scalar_one())

    async def get_one(self, **filter_by: Any) -> ServerMember | None:
        query = select(ServerMemberOrm).filter_by(**filter_by)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ServerMemberDataMapper.to_entity(model) if model else None

    async def update(
        self,
        id_: UUID,
        data: ServerMemberUpdate,
    ) -> ServerMember:
        stmt = (
            update(ServerMemberOrm)
            .where(ServerMemberOrm.id == id_)
            .values(**set_fields(data))
            .returning(ServerMemberOrm)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise NotFoundError
        return ServerMemberDataMapper.to_entity(model)
