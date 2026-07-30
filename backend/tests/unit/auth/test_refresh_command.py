from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.modules.auth.application.commands.refresh import (
    RefreshCommand,
    RefreshCommandHandler,
)
from src.modules.auth.domain.entities.schemas import RefreshTokenCreate
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.infrastructure.security import hash_refresh_token
from tests.unit.auth.fakes import FakeAuthUnitOfWork, FakeRefreshTokenRepository


def _handler() -> tuple[RefreshCommandHandler, FakeRefreshTokenRepository]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    return RefreshCommandHandler(uow), refresh_tokens


async def test_rejects_unknown_token() -> None:
    handler, _ = _handler()

    result = await handler.handle(RefreshCommand(refresh_token="unknown-token"))

    assert result.is_err
    assert isinstance(result.error, InvalidRefreshTokenError)


async def test_rejects_expired_token() -> None:
    handler, refresh_tokens = _handler()
    raw_token = "expired-token"
    await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=uuid4(),
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
    )

    result = await handler.handle(RefreshCommand(refresh_token=raw_token))

    assert result.is_err
    assert isinstance(result.error, InvalidRefreshTokenError)


async def test_rejects_and_revokes_all_on_reused_revoked_token() -> None:
    handler, refresh_tokens = _handler()
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

    result = await handler.handle(RefreshCommand(refresh_token=raw_token))

    assert result.is_err
    assert isinstance(result.error, InvalidRefreshTokenError)


async def test_success_rotates_refresh_token() -> None:
    handler, refresh_tokens = _handler()
    user_id = uuid4()
    raw_token = "valid-token"
    old_token = await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )

    result = await handler.handle(RefreshCommand(refresh_token=raw_token))

    assert result.is_ok
    assert result.value.access_token
    assert result.value.refresh_token
    assert refresh_tokens.tokens[old_token.id].is_revoked
    assert len(refresh_tokens.tokens) == 2
