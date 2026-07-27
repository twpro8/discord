from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.domain.repositories.user_unit_of_work import (
    AbstractUserUnitOfWork,
)
from src.shared.unit_of_work import BaseUnitOfWork


class UserUnitOfWork(BaseUnitOfWork, AbstractUserUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(session)
        self.users = user_repository

    def _uow_marker(self) -> None: ...
