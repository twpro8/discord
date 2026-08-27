from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.core.config import settings
from src.core.security.jwt import create_access_token
from src.modules.auth.adapters.security import (
    create_refresh_token,
    hash_refresh_token,
)
from src.modules.auth.domain.entities.dtos import RefreshTokenCreate, TokenPair
from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.shared.domain.transaction import Transaction


async def issue_tokens(
    refresh_token_repository: RefreshTokenRepository, user_id: UUID
) -> TokenPair:
    access_token = create_access_token(user_id)
    refresh_token, refresh_token_hash = create_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await refresh_token_repository.create(
        RefreshTokenCreate(
            user_id=user_id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


async def get_valid_refresh_token(
    tx: Transaction,
    refresh_token_repository: RefreshTokenRepository,
    refresh_token: str,
) -> RefreshToken:
    """Note the explicit commit before the revoked-token raise: a raised
    exception skips the request's auto-commit entirely (see
    api/v1/dependencies.py::get_transaction), so without this the
    revoke_all write here would be silently discarded instead of
    persisted before the 401 response goes out."""
    token_hash = hash_refresh_token(refresh_token)
    stored = await refresh_token_repository.find_by_hash(token_hash=token_hash)
    if not stored or stored.expires_at <= datetime.now(UTC):
        raise InvalidRefreshTokenError
    if stored.is_revoked:
        await refresh_token_repository.revoke_all(stored.user_id)
        await tx.commit()
        raise InvalidRefreshTokenError
    return stored
