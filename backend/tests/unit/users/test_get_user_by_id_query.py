from uuid import uuid4

from src.modules.users.application.queries.get_user_by_id import (
    GetUserByIDQuery,
    GetUserByIDQueryHandler,
    cache_key,
)
from src.modules.users.domain.exceptions import UserNotFoundError
from tests.unit.users.fakes import FakeCache, FakeUserRepository, make_user


async def test_rejects_unknown_user() -> None:
    handler = GetUserByIDQueryHandler(FakeUserRepository(), FakeCache())

    result = await handler.handle(GetUserByIDQuery(user_id=uuid4()))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_rejects_inactive_user() -> None:
    user = make_user(is_active=False)
    handler = GetUserByIDQueryHandler(FakeUserRepository([user]), FakeCache())

    result = await handler.handle(GetUserByIDQuery(user_id=user.id))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)


async def test_returns_active_user() -> None:
    user = make_user()
    handler = GetUserByIDQueryHandler(FakeUserRepository([user]), FakeCache())

    result = await handler.handle(GetUserByIDQuery(user_id=user.id))

    assert result.is_ok
    assert result.value.id == user.id


async def test_populates_and_reads_through_cache() -> None:
    user = make_user()
    repository = FakeUserRepository([user])
    cache = FakeCache()
    handler = GetUserByIDQueryHandler(repository, cache)

    first = await handler.handle(GetUserByIDQuery(user_id=user.id))
    assert cache_key(user.id) in cache.store

    del repository.users[user.id]
    second = await handler.handle(GetUserByIDQuery(user_id=user.id))

    assert first.is_ok
    assert second.is_ok
    assert second.value == first.value
