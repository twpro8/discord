from dataclasses import dataclass
from uuid import UUID

from src.modules.servers.domain.exceptions import (
    ServerInviteCannotDeleteError,
    ServerInviteNotFoundError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class DeleteInviteCommand(Command):
    server_id: UUID
    user_id: UUID
    code: str


class DeleteInviteCommandHandler:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DeleteInviteCommand) -> Result[None, LumiereError]:
        server = await self._uow.servers.get_one(
            id=command.server_id, owner_id=command.user_id
        )
        if not server:
            return Result.err(ServerInviteCannotDeleteError())

        invite = await self._uow.invites.get_one(
            server_id=command.server_id, code=command.code
        )

        if not invite:
            return Result.err(ServerInviteNotFoundError())

        await self._uow.invites.delete(invite.id)
        await self._uow.commit()
        return Result.ok(None)
