from abc import ABC, abstractmethod

from src.modules.users.domain.repositories.user_repository import UserRepository


class AbstractUserUnitOfWork(ABC):
    users: UserRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
