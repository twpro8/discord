from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerNotEmptyError,
    ServerNotFoundError,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


class DeleteServerUseCase:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._servers = server_repository

    async def __call__(self, *, server_id: UUID, owner_id: UUID) -> None:
        server = await self._servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        if server.member_count > 1:
            raise ServerNotEmptyError

        await self._servers.delete(server.id)
