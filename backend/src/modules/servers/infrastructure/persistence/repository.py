from uuid import UUID

from sqlalchemy import CursorResult, or_, select, update
from sqlalchemy import true as sa_true

from src.modules.servers.domain.entities.server import (
    ServerSchema,
    ServerUserBriefSchema,
)
from src.modules.servers.domain.entities.server_invite import ServerInvite
from src.modules.servers.domain.entities.server_member import ServerMemberSchema
from src.modules.servers.infrastructure.persistence.mappers import (
    ServerInviteMapper,
    ServerMapper,
    ServerMemberMapper,
    ServerUserBriefMapper,
)
from src.modules.servers.infrastructure.persistence.models import (
    ServerInviteOrm,
    ServerMemberOrm,
    ServerOrm,
)
from src.shared.repositories import BaseRepository


class ServerRepository(BaseRepository[ServerOrm, ServerSchema]):
    model = ServerOrm
    schema = ServerSchema
    mapper = ServerMapper

    async def decrement_member_count(self, server_id: UUID) -> ServerSchema:
        statement = (
            update(ServerOrm)
            .where(ServerOrm.id == server_id)
            .values(member_count=ServerOrm.member_count - 1)
            .returning(ServerOrm)
        )
        return await self._execute_and_map_one(statement)

    async def increment_count(self, server_id: UUID) -> ServerSchema:
        statement = (
            update(ServerOrm)
            .where(ServerOrm.id == server_id)
            .values(member_count=ServerOrm.member_count + 1)
            .returning(ServerOrm)
        )
        return await self._execute_and_map_one(statement)

    async def get_servers_where_user_is_member(
        self, user_id: UUID
    ) -> list[ServerUserBriefSchema]:
        statement = (
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

        result = await self.session.execute(statement)
        return [ServerUserBriefMapper.to_schema(model) for model in result.all()]

    async def get_server_where_user_is_member(
        self, user_id: UUID, server_id: UUID
    ) -> ServerSchema | None:
        statement = (
            select(ServerOrm)
            .join(ServerMemberOrm, ServerMemberOrm.server_id == ServerOrm.id)
            .where(
                ServerOrm.id == server_id,
                ServerMemberOrm.user_id == user_id,
                ServerMemberOrm.left_at.is_(None),
            )
        )

        return await self._execute_and_map_one_or_none(statement)


class ServerMemberRepository(BaseRepository[ServerMemberOrm, ServerMemberSchema]):
    model = ServerMemberOrm
    schema = ServerMemberSchema
    mapper = ServerMemberMapper


class ServerInviteRepository(BaseRepository[ServerInviteOrm, ServerInvite]):
    model = ServerInviteOrm
    mapper = ServerInviteMapper

    async def increment_use_count_atomic(
        self, invite_id: UUID, max_uses: int | None
    ) -> int:
        use_count_ok = (
            sa_true() if max_uses is None else self.model.use_count < max_uses
        )
        statement = (
            update(self.model)
            .where(
                self.model.id == invite_id,
                or_(self.model.max_uses.is_(None), use_count_ok),
            )
            .values(use_count=self.model.use_count + 1)
        )

        result: CursorResult = await self.session.execute(statement)  # type: ignore
        return int(result.rowcount) if result.rowcount is not None else 0
