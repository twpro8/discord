from dataclasses import dataclass
from uuid import UUID

from src.modules.servers.domain.entities.dtos import ServerUpdate, ServerUpdateData
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.application.command import Command
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class UpdateServerCommand(Command):
    update_data: ServerUpdateData
    server_id: UUID
    owner_id: UUID


class UpdateServerCommandHandler:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: UpdateServerCommand
    ) -> Result[Server, ServerNotFoundError]:
        server = await self._uow.servers.get_one(
            id=command.server_id, owner_id=command.owner_id
        )
        if not server:
            return Result.err(ServerNotFoundError())

        _update_data = ServerUpdate(
            id=server.id,
            owner_id=command.owner_id,
            name=command.update_data.name,
            description=command.update_data.description,
        )
        updated_server = await self._uow.servers.update(server.id, _update_data)

        await self._uow.commit()
        return Result.ok(updated_server)
