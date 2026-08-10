from src.modules.auth.application.commands.login import (
    LoginCommand,
    LoginCommandHandler,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.shared.errors import TransientError
from tests.unit.auth.fakes import (
    FakeAuthUnitOfWork,
    FakeEmailFacade,
    FakeRefreshTokenRepository,
    FakeUsersFacade,
    make_user,
)


def _handler(
    users: list[User] | None = None,
    email_facade: FakeEmailFacade | None = None,
) -> tuple[LoginCommandHandler, FakeRefreshTokenRepository, FakeEmailFacade]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    email = email_facade or FakeEmailFacade()
    return (
        LoginCommandHandler(uow, FakeUsersFacade(users), email),
        refresh_tokens,
        email,
    )


async def test_rejects_unknown_username() -> None:
    handler, _refresh_tokens, email = _handler()

    result = await handler.handle(LoginCommand(username="ghost", password="12345678"))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)
    assert email.calls == []  # no notification for a login that never happened


async def test_rejects_inactive_user() -> None:
    user = make_user("inactive", is_active=False)
    handler, _refresh_tokens, email = _handler([user])

    result = await handler.handle(
        LoginCommand(username="inactive", password="12345678")
    )

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)
    assert email.calls == []


async def test_rejects_wrong_password() -> None:
    user = make_user("alice", password="correct-password")
    handler, _refresh_tokens, email = _handler([user])

    result = await handler.handle(
        LoginCommand(username="alice", password="wrong-password")
    )

    assert result.is_err
    assert isinstance(result.error, IncorrectPasswordError)
    assert email.calls == []


async def test_success_issues_tokens_and_persists_refresh_token() -> None:
    user = make_user("alice", password="correct-password")
    handler, refresh_tokens, _email = _handler([user])

    result = await handler.handle(
        LoginCommand(username="alice", password="correct-password")
    )

    assert result.is_ok
    tokens = result.value
    assert tokens.access_token
    assert tokens.refresh_token
    assert len(refresh_tokens.tokens) == 1


async def test_success_sends_login_notification_email() -> None:
    user = make_user("alice", password="correct-password")
    handler, _refresh_tokens, email = _handler([user])

    result = await handler.handle(
        LoginCommand(username="alice", password="correct-password")
    )

    assert result.is_ok
    assert len(email.calls) == 1
    call = email.calls[0]
    assert call["to"] == str(user.email)
    assert call["template"] == EmailTemplateName.GENERIC_NOTIFICATION
    assert call["context"]["recipient_name"] == user.name
    assert call["idempotency_key"] is not None
    assert call["idempotency_key"].startswith(f"login-notification:{user.id}:")


async def test_login_notification_failure_does_not_fail_login() -> None:
    user = make_user("alice", password="correct-password")
    failing_email = FakeEmailFacade(error=TransientError("SMTP unreachable"))
    handler, refresh_tokens, email = _handler([user], email_facade=failing_email)

    result = await handler.handle(
        LoginCommand(username="alice", password="correct-password")
    )

    assert result.is_ok  # a broken notification must never block a real login
    assert len(refresh_tokens.tokens) == 1
    assert len(email.calls) == 1
