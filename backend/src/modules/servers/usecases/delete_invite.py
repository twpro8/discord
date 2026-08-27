from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerInviteCannotDeleteError,
    ServerInviteNotFoundError,
)
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


class DeleteInviteUseCase:
    def __init__(
        self,
        server_repository: ServerRepository,
        server_invite_repository: ServerInviteRepository,
    ) -> None:
        self._servers = server_repository
        self._invites = server_invite_repository

    async def __call__(self, *, server_id: UUID, user_id: UUID, code: str) -> None:
        server = await self._servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            raise ServerInviteCannotDeleteError

        invite = await self._invites.get_one(server_id=server_id, code=code)

        if not invite:
            raise ServerInviteNotFoundError

        await self._invites.delete(invite.id)
