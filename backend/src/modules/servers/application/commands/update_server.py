from uuid import UUID

from src.modules.servers.domain.entities.server import (
    Server,
    ServerUpdate,
    ServerUpdateRequest,
)
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork


class UpdateServerCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        update_data: ServerUpdateRequest,
        server_id: UUID,
        owner_id: UUID,
    ) -> Server:
        server = await self._uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        _update_data = ServerUpdate(
            id=server.id,
            owner_id=owner_id,
            **update_data.model_dump(exclude_unset=True),
        )
        updated_server = await self._uow.servers.update(
            server.id, _update_data, exclude_unset=True
        )

        await self._uow.commit()
        return updated_server
