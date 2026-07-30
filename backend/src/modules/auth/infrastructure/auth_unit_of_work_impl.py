from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.auth.infrastructure.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.shared.data.unit_of_work import BaseUnitOfWork


class AuthUnitOfWork(BaseUnitOfWork, AbstractAuthUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        refresh_token_repository: RefreshTokenRepositoryImpl,
    ) -> None:
        super().__init__(session)
        self.refresh_tokens = refresh_token_repository

    def _uow_marker(self) -> None: ...
