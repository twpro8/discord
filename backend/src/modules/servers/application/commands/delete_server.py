from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerNotEmptyError,
    ServerNotFoundError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork


class DeleteServerCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        server_id: UUID,
        owner_id: UUID,
    ) -> None:
        server = await self._uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        if server.member_count > 1:
            raise ServerNotEmptyError

        await self._uow.servers.delete(server.id)
        await self._uow.commit()
