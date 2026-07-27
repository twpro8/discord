from uuid import UUID

from sqlalchemy import select, update

from src.modules.servers.mappers import ServerMapper, ServerUserBriefMapper
from src.modules.servers.models import ServerMemberOrm, ServerOrm
from src.modules.servers.schemas import ServerSchema, ServerUserBriefSchema
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
