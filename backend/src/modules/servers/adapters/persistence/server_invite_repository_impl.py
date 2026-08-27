from collections.abc import Sequence
from dataclasses import asdict
from typing import Any
from uuid import UUID

from sqlalchemy import CursorResult, delete, insert, or_, select, update
from sqlalchemy import true as sa_true
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.adapters.persistence.mappers import (
    ServerInviteDataMapper,
)
from src.modules.servers.adapters.persistence.models import ServerInviteOrm
from src.modules.servers.domain.entities.dtos import ServerInviteCreate
from src.modules.servers.domain.entities.server_invite import ServerInvite


class ServerInviteRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[ServerInvite]:
        query = (
            select(ServerInviteOrm).filter_by(**filter_by).limit(limit).offset(offset)
        )
        result = await self._session.execute(query)
        return [
            ServerInviteDataMapper.to_entity(model) for model in result.scalars().all()
        ]

    async def create(self, data: ServerInviteCreate) -> ServerInvite:
        stmt = insert(ServerInviteOrm).values(**asdict(data)).returning(ServerInviteOrm)
        result = await self._session.execute(stmt)
        return ServerInviteDataMapper.to_entity(result.scalar_one())

    async def get_one(self, **filter_by: Any) -> ServerInvite | None:
        query = select(ServerInviteOrm).filter_by(**filter_by)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ServerInviteDataMapper.to_entity(model) if model else None

    async def delete(self, invite_id: UUID) -> None:
        stmt = delete(ServerInviteOrm).where(ServerInviteOrm.id == invite_id)
        await self._session.execute(stmt)

    async def increment_use_count_atomic(
        self,
        invite_id: UUID,
        max_uses: int | None,
    ) -> int:
        use_count_ok = (
            sa_true() if max_uses is None else ServerInviteOrm.use_count < max_uses
        )
        stmt = (
            update(ServerInviteOrm)
            .where(
                ServerInviteOrm.id == invite_id,
                or_(ServerInviteOrm.max_uses.is_(None), use_count_ok),
            )
            .values(use_count=ServerInviteOrm.use_count + 1)
        )

        result: CursorResult = await self._session.execute(stmt)  # type: ignore
        return int(result.rowcount) if result.rowcount is not None else 0
