import uuid
from datetime import UTC, datetime

from src.modules.users.domain.events.user_registered import UserRegisteredEvent
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.shared.domain.aggregate_root import AggregateRoot


class User(AggregateRoot):
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        username: Username,
        email: Email,
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
        email: Email,
        username: Username,
        password_hash: str,
    ) -> User:
        """Factory encapsulating the invariants of user creation."""
        now = datetime.now(UTC)
        user = cls(
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
        user.record_event(UserRegisteredEvent(user_id=user.id, email=str(email)))
        return user

    def mark_as_inactive(self) -> None:
        self.is_active = False
