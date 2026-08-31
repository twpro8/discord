from src.core.security.hashing import hash_password
from src.modules.users.domain.entities.dtos import UserCreate
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def __call__(
        self, *, name: str, username: str, email: str, plain_password: str
    ) -> User:
        data = UserCreate(
            name=name,
            email=email.strip().lower(),
            username=username.strip(),
            password_hash=hash_password(plain_password),
            avatar_url=None,
            is_active=True,
        )
        return await self._users.create(data)
