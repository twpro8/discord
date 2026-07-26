from sqlalchemy.ext.asyncio import AsyncSession

from src.core.unit_of_work.base_unit_of_work import BaseUnitOfWork
from src.modules.server.repository import ServerRepository


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
