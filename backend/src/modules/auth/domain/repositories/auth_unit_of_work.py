from abc import ABC, abstractmethod

from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.modules.users.domain.repositories.user_repository import UserRepository


class AbstractAuthUnitOfWork(ABC):
    users: UserRepository
    refresh_tokens: RefreshTokenRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
