from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.modules.auth.application.commands.logout import (
    LogoutCommand,
    LogoutCommandHandler,
)
from src.modules.auth.domain.entities.schemas import RefreshTokenCreate
from src.modules.auth.infrastructure.security import hash_refresh_token
from tests.unit.auth.fakes import (
    FakeAuthUnitOfWork,
    FakeRefreshTokenRepository,
    FakeUserRepository,
)


def _handler() -> tuple[LogoutCommandHandler, FakeRefreshTokenRepository]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(FakeUserRepository(), refresh_tokens)
    return LogoutCommandHandler(uow), refresh_tokens


async def test_unknown_token_is_idempotent_ok() -> None:
    handler, _ = _handler()

    result = await handler.handle(LogoutCommand(refresh_token="unknown-token"))

    assert result.is_ok
    assert result.value is None


async def test_revokes_valid_token() -> None:
    handler, refresh_tokens = _handler()
    raw_token = "valid-token"
    token = await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=uuid4(),
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )

    result = await handler.handle(LogoutCommand(refresh_token=raw_token))

    assert result.is_ok
    assert refresh_tokens.tokens[token.id].is_revoked
