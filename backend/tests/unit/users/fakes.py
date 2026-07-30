from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.users.domain.entities.dtos import UserCreate, UserUpdate
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.shared.domain.unset import set_fields


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

    async def create(self, data: UserCreate) -> User:
        raise NotImplementedError

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = self.users[user_id]
        for key, value in set_fields(data).items():
            setattr(user, key, value)
        return user


class FakeUserUnitOfWork(UserUnitOfWork):
    def __init__(self, users: FakeUserRepository) -> None:
        self.users = users
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
