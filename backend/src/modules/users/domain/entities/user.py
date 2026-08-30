import uuid
from datetime import UTC, datetime

from src.shared.domain.entity import Entity


class User(Entity):
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        username: str,
        email: str,
        password_hash: str,
        avatar_url: str | None,
        is_active: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.avatar_url = avatar_url
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def register(
        cls,
        *,
        name: str,
        email: str,
        username: str,
        password_hash: str,
    ) -> User:
        """Factory encapsulating the invariants of user creation."""
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            name=name,
            email=email,
            username=username,
            password_hash=password_hash,
            avatar_url=None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def mark_as_inactive(self) -> None:
        self.is_active = False
