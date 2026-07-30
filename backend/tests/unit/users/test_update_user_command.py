from src.modules.users.application.commands.update_user import (
    UpdateUserCommand,
    UpdateUserCommandHandler,
)
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserUpdate
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
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(name="New Name"),
        )
    )

    assert result.is_ok
    updated = result.value
    assert updated.name == "New Name"
    assert str(updated.username) == "original"
    assert uow.committed


async def test_invalidates_cache() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    handler = UpdateUserCommandHandler(uow, cache)

    await handler.handle(
        UpdateUserCommand(user_id=user.id, data=UserUpdate(name="New Name"))
    )

    assert cache_key(user.id) not in cache.store
