from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.infrastructure.persistence.repository import ServerRepository
from src.modules.servers.invites.repository import ServerInviteRepository
from src.modules.servers.server_members.repository import ServerMemberRepository
from src.shared.unit_of_work.base_unit_of_work import BaseUnitOfWork


class ServerMemberUnitOfWork(BaseUnitOfWork):
    server_members: ServerMemberRepository
    invites: ServerInviteRepository
    servers: ServerRepository

    def __init__(
        self,
        session: AsyncSession,
        server_member_repository: ServerMemberRepository,
        server_invite_repository: ServerInviteRepository,
        server_repository: ServerRepository,
    ) -> None:
        super().__init__(session)
        self.server_members = server_member_repository
        self.invites = server_invite_repository
        self.servers = server_repository

    def _uow_marker(self) -> None: ...
