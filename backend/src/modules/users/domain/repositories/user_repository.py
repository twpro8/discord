import uuid
from typing import Protocol

from pydantic import BaseModel

from src.modules.users.domain.entities.user import User


class UserRepository(Protocol):
    async def create(self, data: BaseModel) -> User: ...

    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def get_by_username(self, username: str) -> User | None: ...

    async def update(
        self,
        user_id: uuid.UUID,
        data: BaseModel,
        exclude_unset: bool = False,
    ) -> User: ...
