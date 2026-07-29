from uuid import UUID

from src.modules.servers.domain.entities.server import (
    Server,
    ServerUpdate,
    UpdateOwnerID,
)
from src.modules.servers.domain.entities.server_member import ServerMemberUpdate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    CannotTransferToSelfError,
    MemberNotFoundError,
    ServerNotFoundError,
    YouAreNotOwnerError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.errors import LumiereError
from src.shared.result import Result


class TransferServerOwnershipCommand:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        server_id: UUID,
        current_user_id: UUID,
        data: UpdateOwnerID,
    ) -> Result[Server, LumiereError]:
        server = await self._uow.servers.get_one(id=server_id)
        if not server:
            return Result.err(ServerNotFoundError())

        current_user = await self._uow.server_members.get_one(
            server_id=server.id,
            user_id=current_user_id,
            left_at=None,
        )

        if not current_user:
            return Result.err(MemberNotFoundError())

        new_owner_id = data.owner_id

        if current_user_id == new_owner_id:
            return Result.err(CannotTransferToSelfError())

        if current_user.role != ServerMemberRole.owner:
            return Result.err(YouAreNotOwnerError())

        new_owner = await self._uow.server_members.get_one(
            server_id=server.id,
            user_id=new_owner_id,
            left_at=None,
        )

        if not new_owner:
            return Result.err(MemberNotFoundError())

        await self._uow.server_members.update(
            current_user.id, ServerMemberUpdate(role=ServerMemberRole.member)
        )

        await self._uow.server_members.update(
            new_owner.id,
            ServerMemberUpdate(role=ServerMemberRole.owner),
        )

        update_server_schema = ServerUpdate(id=server.id, owner_id=new_owner_id)
        new_server = await self._uow.servers.update(
            server.id,
            update_server_schema,
            exclude_unset=True,
        )

        await self._uow.commit()
        return Result.ok(new_server)
