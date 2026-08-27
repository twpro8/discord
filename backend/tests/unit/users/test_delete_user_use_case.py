from uuid import uuid4

import pytest

from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.usecases.delete_user import DeleteUserUseCase
from src.modules.users.usecases.get_user_by_id import cache_key
from tests.unit.fakes import FakeTransaction
from tests.unit.users.fakes import FakeCache, FakeUserRepository, make_user


async def test_rejects_unknown_user() -> None:
    tx = FakeTransaction()
    use_case = DeleteUserUseCase(tx, FakeUserRepository(), FakeCache())

    with pytest.raises(UserNotFoundError):
        await use_case(user_id=uuid4())

    assert not tx.committed


async def test_deactivates_active_user() -> None:
    user = make_user(is_active=True)
    users = FakeUserRepository([user])
    tx = FakeTransaction()
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = DeleteUserUseCase(tx, users, cache)

    await use_case(user_id=user.id)

    assert users.users[user.id].is_active is False
    assert tx.committed
    assert cache_key(user.id) not in cache.store
