from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerInviteCannotDeleteError,
    ServerInviteNotFoundError,
)
from src.modules.servers.infrastructure.unit_of_work import ServerUnitOfWork


class DeleteInviteCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, server_id: UUID, user_id: UUID, code: str) -> None:
        server = await self._uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            raise ServerInviteCannotDeleteError

        invite = await self._uow.invites.get_one(server_id=server_id, code=code)

        if not invite:
            raise ServerInviteNotFoundError

        await self._uow.invites.delete(invite.id)
        await self._uow.commit()
