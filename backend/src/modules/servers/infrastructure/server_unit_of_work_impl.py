from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.data.unit_of_work.base_unit_of_work import BaseUnitOfWork


class ServerUnitOfWorkImpl(BaseUnitOfWork, ServerUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        server_repository: ServerRepository,
        server_member_repository: ServerMemberRepository,
        server_invite_repository: ServerInviteRepository,
    ) -> None:
        super().__init__(session)
        self.servers = server_repository
        self.server_members = server_member_repository
        self.invites = server_invite_repository

    def _uow_marker(self) -> None: ...
