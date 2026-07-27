from sqlalchemy.ext.asyncio import AsyncSession

from src.common.unit_of_work import BaseUnitOfWork
from src.modules.auth.repository import RefreshTokenRepository
from src.modules.users.repository import UserRepository


class AuthUnitOfWork(BaseUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        super().__init__(session)
        self.users = user_repository
        self.refresh_tokens = refresh_token_repository

    def _uow_marker(self) -> None: ...
