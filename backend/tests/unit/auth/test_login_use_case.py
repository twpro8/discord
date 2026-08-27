import pytest

from src.modules.auth.usecases.login import LoginUseCase
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


def _use_case(
    users: list[User] | None = None,
    email_facade: FakeEmailFacade | None = None,
) -> tuple[LoginUseCase, FakeRefreshTokenRepository, FakeEmailFacade]:
    refresh_tokens = FakeRefreshTokenRepository()
    uow = FakeAuthUnitOfWork(refresh_tokens)
    email = email_facade or FakeEmailFacade()
    return (
        LoginUseCase(uow, FakeUsersFacade(users), email),
        refresh_tokens,
        email,
    )


async def test_rejects_unknown_username() -> None:
    use_case, _refresh_tokens, email = _use_case()

    with pytest.raises(UserNotFoundError):
        await use_case(username="ghost", password="12345678")

    assert email.calls == []  # no notification for a login that never happened


async def test_rejects_inactive_user() -> None:
    user = make_user("inactive", is_active=False)
    use_case, _refresh_tokens, email = _use_case([user])

    with pytest.raises(UserNotFoundError):
        await use_case(username="inactive", password="12345678")

    assert email.calls == []


async def test_rejects_wrong_password() -> None:
    user = make_user("alice", password="correct-password")
    use_case, _refresh_tokens, email = _use_case([user])

    with pytest.raises(IncorrectPasswordError):
        await use_case(username="alice", password="wrong-password")

    assert email.calls == []


async def test_success_issues_tokens_and_persists_refresh_token() -> None:
    user = make_user("alice", password="correct-password")
    use_case, refresh_tokens, _email = _use_case([user])

    tokens = await use_case(username="alice", password="correct-password")

    assert tokens.access_token
    assert tokens.refresh_token
    assert len(refresh_tokens.tokens) == 1


async def test_success_sends_login_notification_email() -> None:
    user = make_user("alice", password="correct-password")
    use_case, _refresh_tokens, email = _use_case([user])

    await use_case(username="alice", password="correct-password")

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
    use_case, refresh_tokens, email = _use_case([user], email_facade=failing_email)

    tokens = await use_case(username="alice", password="correct-password")

    assert tokens.access_token  # a broken notification must never block a real login
    assert len(refresh_tokens.tokens) == 1
    assert len(email.calls) == 1
