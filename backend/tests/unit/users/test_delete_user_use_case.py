from uuid import uuid4

import pytest

from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.usecases.delete_user import DeleteUserUseCase
from src.modules.users.usecases.get_user_by_id import cache_key
from tests.unit.users.fakes import (
    FakeCache,
    FakeUserRepository,
    FakeUserUnitOfWork,
    make_user,
)


async def test_rejects_unknown_user() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    use_case = DeleteUserUseCase(uow, FakeCache())

    with pytest.raises(UserNotFoundError):
        await use_case(user_id=uuid4())

    assert not uow.committed


async def test_deactivates_active_user() -> None:
    user = make_user(is_active=True)
    users = FakeUserRepository([user])
    uow = FakeUserUnitOfWork(users)
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = DeleteUserUseCase(uow, cache)

    await use_case(user_id=user.id)

    assert users.users[user.id].is_active is False
    assert uow.committed
    assert cache_key(user.id) not in cache.store
