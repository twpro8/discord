from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.repository import ServerRepository
from src.shared.unit_of_work.base_unit_of_work import BaseUnitOfWork


class ServerUnitOfWork(BaseUnitOfWork):
    servers: ServerRepository

    def __init__(
        self,
        session: AsyncSession,
        server_repository: ServerRepository,
    ) -> None:
        super().__init__(session)
        self.servers = server_repository

    def _uow_marker(self) -> None: ...
