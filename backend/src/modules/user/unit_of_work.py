from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.unit_of_work import BaseUnitOfWork
from src.modules.user.repository import UserRepository


class UserUnitOfWork(BaseUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(session)
        self.users = user_repository

    def _uow_marker(self) -> None: ...
