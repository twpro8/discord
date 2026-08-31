from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.users.domain.entities.dtos import UserCreate, UserUpdate
from src.modules.users.domain.entities.user import User
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
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            name=data.name,
            username=data.username,
            email=data.email,
            password_hash=data.password_hash,
            avatar_url=data.avatar_url,
            is_active=data.is_active,
            created_at=now,
            updated_at=now,
        )
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = self.users[user_id]
        updates = set_fields(data)
        for key, value in updates.items():
            setattr(user, key, value)
        return user


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        self.store[key] = value

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)


class FakeStorage:
    def __init__(self, public_base_url: str = "https://files.example.com") -> None:
        self.objects: dict[str, bytes] = {}
        self._public_base_url = public_base_url

    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.objects[key] = data

    async def download_bytes(self, key: str) -> bytes:
        return self.objects[key]

    async def delete(self, key: str) -> None:
        self.objects.pop(key, None)

    def presigned_upload_url(
        self, key: str, content_type: str | None = None, expires_in: int = 900
    ) -> str:
        return f"{self._public_base_url}/{key}?presigned=1"

    def public_url(self, key: str) -> str:
        return f"{self._public_base_url}/{key}"
