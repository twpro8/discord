import pytest

from src.core.security.hashing import hash_password, verify_password
from src.modules.users.domain.exceptions import IncorrectPasswordError
from src.modules.users.usecases.change_password import ChangePasswordUseCase
from src.modules.users.usecases.get_user_by_id import cache_key
from tests.unit.fakes import FakeTransaction
from tests.unit.users.fakes import FakeCache, FakeUserRepository, make_user


async def test_changes_password_and_invalidates_cache() -> None:
    user = make_user()
    user.password_hash = hash_password("oldpass")
    users = FakeUserRepository([user])
    tx = FakeTransaction()
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = ChangePasswordUseCase(tx, users, cache)

    await use_case(
        user_id=user.id, current_password="oldpass", new_password="newpass123"
    )

    assert verify_password("newpass123", user.password_hash)
    assert tx.committed
    assert cache_key(user.id) not in cache.store


async def test_rejects_wrong_current_password() -> None:
    user = make_user()
    user.password_hash = hash_password("oldpass")
    users = FakeUserRepository([user])
    tx = FakeTransaction()
    use_case = ChangePasswordUseCase(tx, users, FakeCache())

    with pytest.raises(IncorrectPasswordError):
        await use_case(
            user_id=user.id, current_password="wrong", new_password="newpass123"
        )

    assert not tx.committed
