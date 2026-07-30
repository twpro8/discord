import uuid
from typing import Protocol

from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.entities.user import User


class UserRepository(Protocol):
    async def add(self, user: User) -> None: ...

    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def get_by_username(self, username: str) -> User | None: ...

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User: ...
