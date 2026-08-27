from uuid import UUID

from src.modules.servers.domain.entities.dtos import ServerUpdate, ServerUpdateData
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_repository import ServerRepository


class UpdateServerUseCase:
    def __init__(self, server_repository: ServerRepository) -> None:
        self._servers = server_repository

    async def __call__(
        self, *, update_data: ServerUpdateData, server_id: UUID, owner_id: UUID
    ) -> Server:
        server = await self._servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        _update_data = ServerUpdate(
            id=server.id,
            owner_id=owner_id,
            name=update_data.name,
            description=update_data.description,
        )
        return await self._servers.update(server.id, _update_data)
