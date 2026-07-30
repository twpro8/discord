from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.security.hashing import hash_password, verify_password
from src.modules.auth.domain.entities.dtos import RefreshTokenCreate
from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AuthUnitOfWork,
)
from src.modules.users.domain.entities.dtos import UserDTO, user_to_dto
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.shared.errors import LumiereError
from src.shared.result import Result


def make_user(
    username: str, password: str = "12345678", is_active: bool = True
) -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid4(),
        name=username,
        username=Username(username),
        email=Email(f"{username}@test.com"),
        password_hash=hash_password(password),
        avatar_url=None,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


class FakeUsersFacade:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users: dict[UUID, User] = {u.id: u for u in (users or [])}

    async def get_user(self, user_id: UUID) -> UserDTO | None:
        user = self.users.get(user_id)
        return user_to_dto(user) if user else None

    async def get_user_by_username(self, username: str) -> UserDTO | None:
        user = next(
            (u for u in self.users.values() if str(u.username) == username), None
        )
        return user_to_dto(user) if user else None

    async def user_exists(self, user_id: UUID) -> bool:
        return user_id in self.users

    async def create_user(
        self, *, name: str, username: str, email: str, plain_password: str
    ) -> Result[UserDTO, LumiereError]:
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            name=name,
            username=Username(username),
            email=Email(email),
            password_hash=hash_password(plain_password),
            avatar_url=None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.users[user.id] = user
        return Result.ok(user_to_dto(user))

    async def verify_credentials(
        self, *, username: str, plain_password: str
    ) -> Result[UserDTO, LumiereError]:
        user = next(
            (u for u in self.users.values() if str(u.username) == username), None
        )
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())
        if not verify_password(plain_password, user.password_hash):
            return Result.err(IncorrectPasswordError())
        return Result.ok(user_to_dto(user))


class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self.tokens: dict[UUID, RefreshToken] = {}
        self._hash_by_token_id: dict[UUID, str] = {}

    async def create(self, data: RefreshTokenCreate) -> RefreshToken:
        token = RefreshToken(
            id=uuid4(),
            user_id=data.user_id,
            is_revoked=False,
            expires_at=data.expires_at,
            created_at=datetime.now(UTC),
        )
        self.tokens[token.id] = token
        self._hash_by_token_id[token.id] = data.token_hash
        return token

    async def find_by_hash(self, token_hash: str) -> RefreshToken | None:
        for token_id, stored_hash in self._hash_by_token_id.items():
            if stored_hash == token_hash:
                return self.tokens[token_id]
        return None

    async def revoke(self, token_id: UUID) -> None:
        self.tokens[token_id].is_revoked = True

    async def revoke_all(self, user_id: UUID) -> None:
        for token in self.tokens.values():
            if token.user_id == user_id:
                token.is_revoked = True


class FakeAuthUnitOfWork(AuthUnitOfWork):
    def __init__(
        self,
        refresh_tokens: FakeRefreshTokenRepository,
    ) -> None:
        self.refresh_tokens = refresh_tokens
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
