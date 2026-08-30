from src.core.security.hashing import hash_password
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.shared.domain.transaction import Transaction


class CreateUserUseCase:
    def __init__(self, tx: Transaction, user_repository: UserRepository) -> None:
        self._tx = tx
        self._users = user_repository

    async def __call__(
        self, *, name: str, username: str, email: str, plain_password: str
    ) -> User:
        user = User.register(
            name=name,
            email=email.strip().lower(),
            username=username.strip(),
            password_hash=hash_password(plain_password),
        )
        await self._users.add(user)
        await self._tx.commit()

        return user
