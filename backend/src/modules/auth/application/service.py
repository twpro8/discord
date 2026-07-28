from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security.hashing import hash_password, verify_password
from src.core.security.jwt import create_access_token
from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.exceptions import (
    IncorrectPasswordError,
    InvalidRefreshTokenError,
)
from src.modules.auth.domain.schemas import (
    RefreshTokenCreate,
    RegisterForm,
    TokenPair,
)
from src.modules.auth.infrastructure.security import (
    create_refresh_token,
    hash_refresh_token,
)
from src.modules.auth.infrastructure.unit_of_work import AuthUnitOfWork
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.schemas import UserCreate
from src.shared.services import BaseService


class AuthService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        auth_unit_of_work: AuthUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = auth_unit_of_work

    async def register(self, form_data: RegisterForm) -> User:
        user_data = UserCreate(
            **form_data.model_dump(),
            password_hash=hash_password(form_data.password),
        )
        user = await self.uow.users.create(user_data)
        await self.session.commit()
        return user

    async def login(self, username: str, password: str) -> TokenPair:
        user = await self.uow.users.get_by_username(username)
        if not user or not user.is_active:
            raise UserNotFoundError
        if not verify_password(password, user.password_hash):
            raise IncorrectPasswordError
        tokens = await self._issue_tokens(user.id)
        await self.session.commit()
        return TokenPair(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        stored = await self._get_valid_refresh_token(refresh_token)
        # Refresh Token Rotation
        await self.uow.refresh_tokens.revoke(stored.id)
        tokens = await self._issue_tokens(stored.user_id)
        await self.uow.commit()
        return tokens

    async def logout(self, refresh_token: str) -> None:
        try:
            stored = await self._get_valid_refresh_token(refresh_token)
        except InvalidRefreshTokenError:
            return
        await self.uow.refresh_tokens.revoke(stored.id)
        await self.uow.commit()

    async def _issue_tokens(self, user_id: UUID) -> TokenPair:
        access_token = create_access_token(user_id)
        refresh_token, refresh_token_hash = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.uow.refresh_tokens.create(
            RefreshTokenCreate(
                user_id=user_id,
                token_hash=refresh_token_hash,
                expires_at=expires_at,
            )
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def _get_valid_refresh_token(self, refresh_token: str) -> RefreshToken:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.uow.refresh_tokens.get_one(token_hash=token_hash)
        if not stored or stored.expires_at <= datetime.now(UTC):
            raise InvalidRefreshTokenError
        if stored.is_revoked:
            # Reuse detected - potential token theft, revoke all user sessions
            await self.uow.refresh_tokens.revoke_all(stored.user_id)
            await self.uow.commit()
            raise InvalidRefreshTokenError
        return stored
