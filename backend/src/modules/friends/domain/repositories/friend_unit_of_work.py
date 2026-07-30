from abc import ABC, abstractmethod

from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class FriendUnitOfWork(ABC):
    friends: FriendRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
