from uuid import UUID

from src.modules.servers.domain.entities.server import (
    ServerSchema,
    ServerUpdateRequestSchema,
    ServerUpdateSchema,
)
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.infrastructure.unit_of_work import ServerUnitOfWork


class UpdateServerCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        update_data: ServerUpdateRequestSchema,
        server_id: UUID,
        owner_id: UUID,
    ) -> ServerSchema:
        server = await self._uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        merged_data = server.model_dump() | update_data.model_dump(exclude_unset=True)
        merged_data["id"] = server.id
        merged_data["owner_id"] = owner_id

        _update_data = ServerUpdateSchema(**merged_data)
        updated_server = await self._uow.servers.update(server.id, _update_data)

        await self._uow.commit()
        return updated_server
