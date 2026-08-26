from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.modules.auth.domain.entities.dtos import RefreshTokenCreate
from src.modules.auth.infrastructure.security import hash_refresh_token
from src.modules.auth.usecases.logout import LogoutUseCase
from tests.unit.auth.fakes import FakeAuthUnitOfWork, FakeRefreshTokenRepository


def _use_case() -> tuple[LogoutUseCase, FakeRefreshTokenRepository]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    return LogoutUseCase(uow), refresh_tokens


async def test_unknown_token_is_idempotent_ok() -> None:
    use_case, _ = _use_case()

    await use_case(refresh_token="unknown-token")


async def test_revokes_valid_token() -> None:
    use_case, refresh_tokens = _use_case()
    raw_token = "valid-token"
    token = await refresh_tokens.create(
        RefreshTokenCreate(
            user_id=uuid4(),
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )

    await use_case(refresh_token=raw_token)

    assert refresh_tokens.tokens[token.id].is_revoked
