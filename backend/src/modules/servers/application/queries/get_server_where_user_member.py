from dataclasses import dataclass
from uuid import UUID

from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.shared.application.query import Query
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetServerWhereUserMemberQuery(Query):
    user_id: UUID
    server_id: UUID


class GetServerWhereUserMemberQueryHandler:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._server_repository = server_repository

    async def handle(
        self, query: GetServerWhereUserMemberQuery
    ) -> Result[Server, ServerNotFoundError]:
        result = await self._server_repository.get_server_where_user_is_member(
            user_id=query.user_id,
            server_id=query.server_id,
        )

        if not result:
            return Result.err(ServerNotFoundError())

        return Result.ok(result)
