from src.core.security.hashing import verify_password
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.modules.users.domain.repositories.user_repository import UserRepository


class VerifyCredentialsUseCase:
    """Owns the "how is a password verified" invariant. Callers (e.g. auth)
    only ever see a User/error via this use case — never a password_hash."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def __call__(self, *, username: str, plain_password: str) -> User:
        user = await self._users.get_by_username(username)
        if user is None or not user.is_active:
            raise UserNotFoundError
        if not verify_password(plain_password, user.password_hash):
            raise IncorrectPasswordError
        return user
