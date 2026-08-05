from dataclasses import asdict
from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain.entities.dtos import (
    ServerMemberCreate,
    ServerMemberUpdate,
    ServerMemberWithUser,
)
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.infrastructure.persistence.mappers import (
    ServerMemberDataMapper,
)
from src.modules.servers.infrastructure.persistence.models import ServerMemberOrm
from src.modules.users.infrastructure.persistence.models import UserOrm
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

    async def list_with_users(self, server_id: UUID) -> list[ServerMemberWithUser]:
        query = (
            select(
                ServerMemberOrm.id,
                ServerMemberOrm.user_id,
                UserOrm.username,
                UserOrm.avatar_url,
                ServerMemberOrm.role,
            )
            .join(UserOrm, UserOrm.id == ServerMemberOrm.user_id)
            .where(
                ServerMemberOrm.server_id == server_id,
                ServerMemberOrm.left_at.is_(None),
            )
        )
        rows = (await self._session.execute(query)).all()
        return [
            ServerMemberWithUser(
                id=row.id,
                user_id=row.user_id,
                username=row.username,
                avatar_url=row.avatar_url,
                role=ServerMemberRole(row.role),
            )
            for row in rows
        ]

    async def list_server_ids_for_user(self, user_id: UUID) -> set[UUID]:
        query = select(ServerMemberOrm.server_id).where(
            ServerMemberOrm.user_id == user_id,
            ServerMemberOrm.left_at.is_(None),
        )
        result = await self._session.execute(query)
        return set(result.scalars().all())

    async def list_user_ids(self, server_id: UUID) -> set[UUID]:
        query = select(ServerMemberOrm.user_id).where(
            ServerMemberOrm.server_id == server_id,
            ServerMemberOrm.left_at.is_(None),
        )
        result = await self._session.execute(query)
        return set(result.scalars().all())
