from src.modules.auth.application.commands.login import (
    LoginCommand,
    LoginCommandHandler,
)
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from tests.unit.auth.fakes import (
    FakeAuthUnitOfWork,
    FakeRefreshTokenRepository,
    FakeUsersFacade,
    make_user,
)


def _handler(
    users: list[User] | None = None,
) -> tuple[LoginCommandHandler, FakeRefreshTokenRepository]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    return LoginCommandHandler(uow, FakeUsersFacade(users)), refresh_tokens


async def test_rejects_unknown_username() -> None:
    handler, _ = _handler()

    result = await handler.handle(LoginCommand(username="ghost", password="12345678"))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_rejects_inactive_user() -> None:
    user = make_user("inactive", is_active=False)
    handler, _ = _handler([user])

    result = await handler.handle(
        LoginCommand(username="inactive", password="12345678")
    )

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_rejects_wrong_password() -> None:
    user = make_user("alice", password="correct-password")
    handler, _ = _handler([user])

    result = await handler.handle(
        LoginCommand(username="alice", password="wrong-password")
    )

    assert result.is_err
    assert isinstance(result.error, IncorrectPasswordError)


async def test_success_issues_tokens_and_persists_refresh_token() -> None:
    user = make_user("alice", password="correct-password")
    handler, refresh_tokens = _handler([user])

    result = await handler.handle(
        LoginCommand(username="alice", password="correct-password")
    )

    assert result.is_ok
    tokens = result.value
    assert tokens.access_token
    assert tokens.refresh_token
    assert len(refresh_tokens.tokens) == 1
