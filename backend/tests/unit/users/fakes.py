from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import (
    AbstractUserUnitOfWork,
)


def make_user(username: str = "alice", is_active: bool = True) -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid4(),
        name=username,
        username=username,
        email=f"{username}@test.com",
        password_hash="hash",
        avatar_url=None,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users: dict[UUID, User] = {u.id: u for u in (users or [])}

    async def create(self, data: BaseModel) -> User:
        raise NotImplementedError

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    async def update(
        self,
        user_id: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
    ) -> User:
        user = self.users[user_id]
        for key, value in data.model_dump(exclude_unset=exclude_unset).items():
            setattr(user, key, value)
        return user


class FakeUserUnitOfWork(AbstractUserUnitOfWork):
    def __init__(self, users: FakeUserRepository) -> None:
        self.users = users
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
