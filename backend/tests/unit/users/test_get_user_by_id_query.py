from uuid import uuid4

from src.modules.users.application.queries.get_user_by_id import (
    GetUserByIDQuery,
    GetUserByIDQueryHandler,
)
from src.modules.users.domain.exceptions import UserNotFoundError
from tests.unit.users.fakes import FakeUserRepository, make_user


async def test_rejects_unknown_user() -> None:
    handler = GetUserByIDQueryHandler(FakeUserRepository())

    result = await handler.handle(GetUserByIDQuery(user_id=uuid4()))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_rejects_inactive_user() -> None:
    user = make_user(is_active=False)
    handler = GetUserByIDQueryHandler(FakeUserRepository([user]))

    result = await handler.handle(GetUserByIDQuery(user_id=user.id))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_returns_active_user() -> None:
    user = make_user()
    handler = GetUserByIDQueryHandler(FakeUserRepository([user]))

    result = await handler.handle(GetUserByIDQuery(user_id=user.id))

    assert result.is_ok
    assert result.value.id == user.id
