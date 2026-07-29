from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain.entities.server_member import (
    ServerMember,
    ServerMemberCreate,
    ServerMemberUpdate,
)
from src.modules.servers.infrastructure.persistence.mappers import (
    ServerMemberDataMapper,
)
from src.modules.servers.infrastructure.persistence.models import ServerMemberOrm
from src.shared.errors import NotFoundError


class ServerMemberRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ServerMemberCreate) -> ServerMember:
        stmt = (
            insert(ServerMemberOrm)
            .values(**data.model_dump())
            .returning(ServerMemberOrm)
        )
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
        exclude_unset: bool = False,
    ) -> ServerMember:
        stmt = (
            update(ServerMemberOrm)
            .where(ServerMemberOrm.id == id_)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(ServerMemberOrm)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise NotFoundError
        return ServerMemberDataMapper.to_entity(model)
