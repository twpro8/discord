from uuid import UUID

from sqlalchemy import update, select
from sqlalchemy.orm import selectinload
from src.core.repositories import BaseRepository
from src.server.mappers import ServerMapper, ServerUserBriefMapper
from src.server.models import ServerMemberOrm, ServerOrm
from src.server.schemas import ServerSchema, ServerUserBriefSchema


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
