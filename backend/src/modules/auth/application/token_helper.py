from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.core.config import settings
from src.core.security.jwt import create_access_token
from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.auth.domain.schemas import RefreshTokenCreate, TokenPair
from src.modules.auth.infrastructure.security import (
    create_refresh_token,
    hash_refresh_token,
)


async def issue_tokens(uow: AbstractAuthUnitOfWork, user_id: UUID) -> TokenPair:
    access_token = create_access_token(user_id)
    refresh_token, refresh_token_hash = create_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await uow.refresh_tokens.create(
        RefreshTokenCreate(
            user_id=user_id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


async def get_valid_refresh_token(
    uow: AbstractAuthUnitOfWork, refresh_token: str
) -> RefreshToken:
    token_hash = hash_refresh_token(refresh_token)
    stored = await uow.refresh_tokens.find_by_hash(token_hash=token_hash)
    if not stored or stored.expires_at <= datetime.now(UTC):
        raise InvalidRefreshTokenError
    if stored.is_revoked:
        await uow.refresh_tokens.revoke_all(stored.user_id)
        await uow.commit()
        raise InvalidRefreshTokenError
    return stored
