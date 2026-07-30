from collections.abc import Sequence
from dataclasses import asdict
from typing import Any
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain.entities.server import (
    Server,
    ServerCreate,
    ServerUpdate,
    ServerUserSummary,
)
from src.modules.servers.infrastructure.persistence.mappers import (
    ServerDataMapper,
    ServerUserSummaryDataMapper,
)
from src.modules.servers.infrastructure.persistence.models import (
    ServerMemberOrm,
    ServerOrm,
)
from src.shared.domain.unset import set_fields
from src.shared.errors import NotFoundError


class ServerRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ServerCreate) -> Server:
        stmt = insert(ServerOrm).values(**asdict(data)).returning(ServerOrm)
        result = await self._session.execute(stmt)
        return ServerDataMapper.to_entity(result.scalar_one())

    async def get_one(self, **filter_by: Any) -> Server | None:
        query = select(ServerOrm).filter_by(**filter_by)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ServerDataMapper.to_entity(model) if model else None

    async def update(
        self,
        server_id: UUID,
        data: ServerUpdate,
    ) -> Server:
        stmt = (
            update(ServerOrm)
            .where(ServerOrm.id == server_id)
            .values(**set_fields(data))
            .returning(ServerOrm)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise NotFoundError
        return ServerDataMapper.to_entity(model)

    async def delete(self, server_id: UUID) -> None:
        stmt = delete(ServerOrm).where(ServerOrm.id == server_id)
        await self._session.execute(stmt)

    async def decrement_member_count(self, server_id: UUID) -> Server:
        stmt = (
            update(ServerOrm)
            .where(ServerOrm.id == server_id)
            .values(member_count=ServerOrm.member_count - 1)
            .returning(ServerOrm)
        )
        result = await self._session.execute(stmt)
        return ServerDataMapper.to_entity(result.scalar_one())

    async def increment_count(self, server_id: UUID) -> Server:
        stmt = (
            update(ServerOrm)
            .where(ServerOrm.id == server_id)
            .values(member_count=ServerOrm.member_count + 1)
            .returning(ServerOrm)
        )
        result = await self._session.execute(stmt)
        return ServerDataMapper.to_entity(result.scalar_one())

    async def get_servers_where_user_is_member(
        self,
        user_id: UUID,
    ) -> list[ServerUserSummary]:
        stmt = (
            select(
                ServerOrm.id,
                ServerOrm.name,
                ServerOrm.icon_url,
                ServerOrm.owner_id,
                ServerOrm.member_count,
                ServerMemberOrm.role,
                ServerMemberOrm.joined_at,
            )
            .join(ServerMemberOrm, ServerMemberOrm.server_id == ServerOrm.id)
            .where(
                ServerMemberOrm.user_id == user_id, ServerMemberOrm.left_at.is_(None)
            )
            .order_by(ServerMemberOrm.joined_at.desc())
        )

        result = await self._session.execute(stmt)
        return [ServerUserSummaryDataMapper.to_entity(model) for model in result.all()]

    async def get_server_where_user_is_member(
        self,
        user_id: UUID,
        server_id: UUID,
    ) -> Server | None:
        stmt = (
            select(ServerOrm)
            .join(ServerMemberOrm, ServerMemberOrm.server_id == ServerOrm.id)
            .where(
                ServerOrm.id == server_id,
                ServerMemberOrm.user_id == user_id,
                ServerMemberOrm.left_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ServerDataMapper.to_entity(model) if model else None

    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[Server]:
        query = select(ServerOrm).filter_by(**filter_by).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return [ServerDataMapper.to_entity(model) for model in result.scalars().all()]
