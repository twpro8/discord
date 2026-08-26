from uuid import UUID

from src.modules.servers.domain.entities.dtos import ServerMemberUpdate, ServerUpdate
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    CannotTransferToSelfError,
    MemberNotFoundError,
    ServerNotFoundError,
    YouAreNotOwnerError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork


class TransferServerOwnershipUseCase:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, *, server_id: UUID, current_user_id: UUID, new_owner_id: UUID
    ) -> Server:
        server = await self._uow.servers.get_one(id=server_id)
        if not server:
            raise ServerNotFoundError

        current_user = await self._uow.server_members.get_one(
            server_id=server.id,
            user_id=current_user_id,
            left_at=None,
        )

        if not current_user:
            raise MemberNotFoundError

        if current_user_id == new_owner_id:
            raise CannotTransferToSelfError

        if current_user.role != ServerMemberRole.owner:
            raise YouAreNotOwnerError

        new_owner = await self._uow.server_members.get_one(
            server_id=server.id,
            user_id=new_owner_id,
            left_at=None,
        )

        if not new_owner:
            raise MemberNotFoundError

        await self._uow.server_members.update(
            current_user.id, ServerMemberUpdate(role=ServerMemberRole.member)
        )

        await self._uow.server_members.update(
            new_owner.id,
            ServerMemberUpdate(role=ServerMemberRole.owner),
        )

        update_server_schema = ServerUpdate(id=server.id, owner_id=new_owner_id)
        new_server = await self._uow.servers.update(server.id, update_server_schema)

        await self._uow.commit()
        return new_server
