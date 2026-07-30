from dataclasses import dataclass
from uuid import UUID

from src.modules.servers.domain.entities.dtos import ServerUserSummary
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetServersWhereUserMemberQuery(Query):
    user_id: UUID


class GetServersWhereUserMemberQueryHandler:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._server_repository = server_repository

    async def handle(
        self, query: GetServersWhereUserMemberQuery
    ) -> Result[list[ServerUserSummary], LumiereError]:
        servers = await self._server_repository.get_servers_where_user_is_member(
            query.user_id
        )
        return Result.ok(servers)
