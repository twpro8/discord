import pytest

from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import (
    InvalidEmail,
    InvalidUsername,
    UserAlreadyExistsError,
)
from src.modules.users.usecases.get_user_by_id import cache_key
from src.modules.users.usecases.update_user import UpdateUserUseCase
from tests.unit.users.fakes import (
    FakeCache,
    FakeUserRepository,
    FakeUserUnitOfWork,
    make_user,
)


async def test_partial_update_only_touches_provided_fields() -> None:
    user = make_user(username="original")
    users = FakeUserRepository([user])
    uow = FakeUserUnitOfWork(users)
    use_case = UpdateUserUseCase(uow, FakeCache())

    updated = await use_case(user_id=user.id, data=UserUpdate(name="New Name"))

    assert updated.name == "New Name"
    assert str(updated.username) == "original"
    assert uow.committed


async def test_invalidates_cache() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = UpdateUserUseCase(uow, cache)

    await use_case(user_id=user.id, data=UserUpdate(name="New Name"))

    assert cache_key(user.id) not in cache.store


async def test_rejects_username_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    uow = FakeUserUnitOfWork(FakeUserRepository([user, other]))
    use_case = UpdateUserUseCase(uow, FakeCache())

    with pytest.raises(UserAlreadyExistsError):
        await use_case(user_id=user.id, data=UserUpdate(username="bob"))

    assert not uow.committed


async def test_allows_keeping_own_username() -> None:
    user = make_user(username="alice")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateUserUseCase(uow, FakeCache())

    updated = await use_case(user_id=user.id, data=UserUpdate(username="alice"))

    assert str(updated.username) == "alice"


async def test_rejects_email_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    uow = FakeUserUnitOfWork(FakeUserRepository([user, other]))
    use_case = UpdateUserUseCase(uow, FakeCache())

    with pytest.raises(UserAlreadyExistsError):
        await use_case(user_id=user.id, data=UserUpdate(email="bob@test.com"))


async def test_rejects_invalid_username_value() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateUserUseCase(uow, FakeCache())

    with pytest.raises(InvalidUsername):
        await use_case(user_id=user.id, data=UserUpdate(username="ab"))


async def test_rejects_invalid_email_value() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateUserUseCase(uow, FakeCache())

    with pytest.raises(InvalidEmail):
        await use_case(user_id=user.id, data=UserUpdate(email="not-an-email"))
