from dataclasses import dataclass

from src.core.security.hashing import verify_password
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class VerifyCredentialsQuery(Query):
    username: str
    plain_password: str


class VerifyCredentialsQueryHandler:
    """Owns the "how is a password verified" invariant. Callers (e.g. auth)
    only ever see a User/error via this query — never a password_hash."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def handle(self, query: VerifyCredentialsQuery) -> Result[User, LumiereError]:
        user = await self._users.get_by_username(query.username)
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())
        if not verify_password(query.plain_password, user.password_hash):
            return Result.err(IncorrectPasswordError())
        return Result.ok(user)
