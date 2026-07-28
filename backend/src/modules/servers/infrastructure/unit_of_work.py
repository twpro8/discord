from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.infrastructure.persistence.repository import (
    ServerInviteRepository,
    ServerMemberRepository,
    ServerRepository,
)
from src.shared.unit_of_work.base_unit_of_work import BaseUnitOfWork


class ServerUnitOfWork(BaseUnitOfWork):
    servers: ServerRepository
    server_members: ServerMemberRepository
    invites: ServerInviteRepository

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
