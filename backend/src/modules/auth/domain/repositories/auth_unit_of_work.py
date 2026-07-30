from abc import ABC, abstractmethod

from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)


class AbstractAuthUnitOfWork(ABC):
    refresh_tokens: RefreshTokenRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
