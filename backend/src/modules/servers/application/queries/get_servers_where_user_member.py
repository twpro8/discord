from uuid import UUID

from src.modules.servers.domain.entities.server import ServerUserSummary
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.shared.errors import LumiereError
from src.shared.result import Result


class GetServersWhereUserMemberQuery:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._server_repository = server_repository

    async def __call__(
        self, user_id: UUID
    ) -> Result[list[ServerUserSummary], LumiereError]:
        servers = await self._server_repository.get_servers_where_user_is_member(
            user_id
        )
        return Result.ok(servers)
