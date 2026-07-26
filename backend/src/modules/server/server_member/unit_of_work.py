from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.unit_of_work.base_unit_of_work import BaseUnitOfWork
from src.modules.server.invite.repository import ServerInviteRepository
from src.modules.server.repository import ServerRepository
from src.modules.server.server_member.repository import ServerMemberRepository


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
