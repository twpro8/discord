from uuid import UUID

from src.modules.servers.domain.entities.server import ServerSchema
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.infrastructure.persistence.repository import ServerRepository


class GetServerWhereUserMemberQuery:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._server_repository = server_repository

    async def __call__(self, user_id: UUID, server_id: UUID) -> ServerSchema:
        result = await self._server_repository.get_server_where_user_is_member(
            user_id, server_id
        )

        if not result:
            raise ServerNotFoundError

        return result
