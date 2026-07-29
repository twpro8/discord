from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerNotEmptyError,
    ServerNotFoundError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.errors import LumiereError
from src.shared.result import Result


class DeleteServerCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        server_id: UUID,
        owner_id: UUID,
    ) -> Result[None, LumiereError]:
        server = await self._uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            return Result.err(ServerNotFoundError())

        if server.member_count > 1:
            return Result.err(ServerNotEmptyError())

        await self._uow.servers.delete(server.id)
        await self._uow.commit()
        return Result.ok(None)
