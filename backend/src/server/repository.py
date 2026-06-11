from uuid import UUID

from sqlalchemy import update
from src.core.repositories import BaseRepository
from src.server.mappers import ServerMapper
from src.server.models import ServerOrm
from src.server.schemas import ServerSchema


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
