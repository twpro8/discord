from abc import ABC, abstractmethod

from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.modules.users.domain.repositories.user_repository import UserRepository


class FriendUnitOfWork(ABC):
    friends: FriendRepository
    users: UserRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
