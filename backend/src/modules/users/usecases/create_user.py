from src.core.event_bus import EventBus
from src.core.security.hashing import hash_password
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.shared.domain.transaction import Transaction


class CreateUserUseCase:
    def __init__(
        self, tx: Transaction, user_repository: UserRepository, event_bus: EventBus
    ) -> None:
        self._tx = tx
        self._users = user_repository
        self._event_bus = event_bus

    async def __call__(
        self, *, name: str, username: str, email: str, plain_password: str
    ) -> User:
        user = User.register(
            name=name,
            email=Email(email),
            username=Username(username),
            password_hash=hash_password(plain_password),
        )
        await self._users.add(user)
        await self._tx.commit()

        await self._event_bus.publish_many(user.pull_events())
        return user
