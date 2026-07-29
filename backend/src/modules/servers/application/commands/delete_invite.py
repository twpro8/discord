from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerInviteCannotDeleteError,
    ServerInviteNotFoundError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.errors import LumiereError
from src.shared.result import Result


class DeleteInviteCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, server_id: UUID, user_id: UUID, code: str
    ) -> Result[None, LumiereError]:
        server = await self._uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            return Result.err(ServerInviteCannotDeleteError())

        invite = await self._uow.invites.get_one(server_id=server_id, code=code)

        if not invite:
            return Result.err(ServerInviteNotFoundError())

        await self._uow.invites.delete(invite.id)
        await self._uow.commit()
        return Result.ok(None)
