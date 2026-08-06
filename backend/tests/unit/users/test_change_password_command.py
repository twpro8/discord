from src.core.security.hashing import hash_password, verify_password
from src.modules.users.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
)
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.exceptions import IncorrectPasswordError
from tests.unit.users.fakes import (
    FakeCache,
    FakeUserRepository,
    FakeUserUnitOfWork,
    make_user,
)


async def test_changes_password_and_invalidates_cache() -> None:
    user = make_user()
    user.password_hash = hash_password("oldpass")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    handler = ChangePasswordCommandHandler(uow, cache)

    result = await handler.handle(
        ChangePasswordCommand(
            user_id=user.id,
            current_password="oldpass",
            new_password="newpass123",
        )
    )

    assert result.is_ok
    assert verify_password("newpass123", user.password_hash)
    assert uow.committed
    assert cache_key(user.id) not in cache.store


async def test_rejects_wrong_current_password() -> None:
    user = make_user()
    user.password_hash = hash_password("oldpass")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    handler = ChangePasswordCommandHandler(uow, FakeCache())

    result = await handler.handle(
        ChangePasswordCommand(
            user_id=user.id,
            current_password="wrong",
            new_password="newpass123",
        )
    )

    assert result.is_err
    assert isinstance(result.error, IncorrectPasswordError)
    assert not uow.committed
