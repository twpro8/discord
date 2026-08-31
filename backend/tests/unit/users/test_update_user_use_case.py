import pytest

from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import UserAlreadyExistsError
from src.modules.users.usecases.get_user_by_id import cache_key
from src.modules.users.usecases.update_user import UpdateUserUseCase
from tests.unit.fakes import FakeTransaction
from tests.unit.users.fakes import FakeCache, FakeUserRepository, make_user


async def test_partial_update_only_touches_provided_fields() -> None:
    user = make_user(username="original")
    users = FakeUserRepository([user])
    tx = FakeTransaction()
    use_case = UpdateUserUseCase(tx, users, FakeCache())

    updated = await use_case(user_id=user.id, data=UserUpdate(name="New Name"))

    assert updated.name == "New Name"
    assert updated.username == "original"
    assert tx.committed


async def test_invalidates_cache() -> None:
    user = make_user()
    tx = FakeTransaction()
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = UpdateUserUseCase(tx, FakeUserRepository([user]), cache)

    await use_case(user_id=user.id, data=UserUpdate(name="New Name"))

    assert cache_key(user.id) not in cache.store


async def test_rejects_username_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    tx = FakeTransaction()
    use_case = UpdateUserUseCase(tx, FakeUserRepository([user, other]), FakeCache())

    with pytest.raises(UserAlreadyExistsError):
        await use_case(user_id=user.id, data=UserUpdate(username="bob"))

    assert not tx.committed


async def test_allows_keeping_own_username() -> None:
    user = make_user(username="alice")
    tx = FakeTransaction()
    use_case = UpdateUserUseCase(tx, FakeUserRepository([user]), FakeCache())

    updated = await use_case(user_id=user.id, data=UserUpdate(username="alice"))

    assert updated.username == "alice"


async def test_rejects_email_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    tx = FakeTransaction()
    use_case = UpdateUserUseCase(tx, FakeUserRepository([user, other]), FakeCache())

    with pytest.raises(UserAlreadyExistsError):
        await use_case(user_id=user.id, data=UserUpdate(email="bob@test.com"))


async def test_normalizes_username_and_email_before_persisting() -> None:
    user = make_user(username="alice")
    users = FakeUserRepository([user])
    tx = FakeTransaction()
    use_case = UpdateUserUseCase(tx, users, FakeCache())

    updated = await use_case(
        user_id=user.id,
        data=UserUpdate(username="  bob  ", email="  Bob@Example.COM  "),
    )

    assert updated.username == "bob"
    assert updated.email == "bob@example.com"
