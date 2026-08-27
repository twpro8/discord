from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.modules.auth.domain.entities.dtos import RefreshTokenCreate
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.infrastructure.security import hash_refresh_token
from src.modules.auth.usecases.refresh import RefreshUseCase
from tests.unit.auth.fakes import FakeAuthUnitOfWork, FakeRefreshTokenRepository


def _use_case() -> tuple[RefreshUseCase, FakeRefreshTokenRepository]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    return RefreshUseCase(uow), refresh_tokens


async def test_rejects_unknown_token() -> None:
    use_case, _ = _use_case()

    with pytest.raises(InvalidRefreshTokenError):
        await use_case(refresh_token="unknown-token")


async def test_rejects_expired_token() -> None:
    use_case, refresh_tokens = _use_case()
    raw_token = "expired-token"
    await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=uuid4(),
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
    )

    with pytest.raises(InvalidRefreshTokenError):
        await use_case(refresh_token=raw_token)


async def test_rejects_and_revokes_all_on_reused_revoked_token() -> None:
    use_case, refresh_tokens = _use_case()
    user_id = uuid4()
    raw_token = "revoked-token"
    token = await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )
    await refresh_tokens.revoke(token.id)

    with pytest.raises(InvalidRefreshTokenError):
        await use_case(refresh_token=raw_token)


async def test_success_rotates_refresh_token() -> None:
    use_case, refresh_tokens = _use_case()
    user_id = uuid4()
    raw_token = "valid-token"
    old_token = await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )

    tokens = await use_case(refresh_token=raw_token)

    assert tokens.access_token
    assert tokens.refresh_token
    assert refresh_tokens.tokens[old_token.id].is_revoked
    assert len(refresh_tokens.tokens) == 2
