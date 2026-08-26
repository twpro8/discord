from uuid import uuid4

import pytest

from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.usecases.get_user_by_id import GetUserByIDUseCase, cache_key
from tests.unit.users.fakes import FakeCache, FakeUserRepository, make_user


async def test_rejects_unknown_user() -> None:
    use_case = GetUserByIDUseCase(FakeUserRepository(), FakeCache())

    with pytest.raises(UserNotFoundError):
        await use_case(user_id=uuid4())


async def test_rejects_inactive_user() -> None:
    user = make_user(is_active=False)
    use_case = GetUserByIDUseCase(FakeUserRepository([user]), FakeCache())

    with pytest.raises(UserNotFoundError):
        await use_case(user_id=user.id)


async def test_returns_active_user() -> None:
    user = make_user()
    use_case = GetUserByIDUseCase(FakeUserRepository([user]), FakeCache())

    dto = await use_case(user_id=user.id)

    assert dto.id == user.id


async def test_populates_and_reads_through_cache() -> None:
    user = make_user()
    repository = FakeUserRepository([user])
    cache = FakeCache()
    use_case = GetUserByIDUseCase(repository, cache)

    first = await use_case(user_id=user.id)
    assert cache_key(user.id) in cache.store

    del repository.users[user.id]
    second = await use_case(user_id=user.id)

    assert second == first
