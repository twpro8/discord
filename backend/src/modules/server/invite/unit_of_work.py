from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.unit_of_work.base_unit_of_work import BaseUnitOfWork
from src.modules.server.invite.repository import ServerInviteRepository
from src.modules.server.repository import ServerRepository


class ServerInviteUnitOfWork(BaseUnitOfWork):
    invites: ServerInviteRepository
    servers: ServerRepository

    def __init__(
        self,
        session: AsyncSession,
        server_invite_repository: ServerInviteRepository,
        server_repository: ServerRepository,
    ) -> None:
        super().__init__(session)
        self.invites = server_invite_repository
        self.servers = server_repository

    def _uow_marker(self) -> None: ...
