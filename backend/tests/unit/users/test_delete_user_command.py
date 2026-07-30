from uuid import uuid4

from src.modules.users.application.commands.delete_user import (
    DeleteUserCommand,
    DeleteUserCommandHandler,
)
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.exceptions import UserNotFoundError
from tests.unit.users.fakes import (
    FakeCache,
    FakeUserRepository,
    FakeUserUnitOfWork,
    make_user,
)


async def test_rejects_unknown_user() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    handler = DeleteUserCommandHandler(uow, FakeCache())

    result = await handler.handle(DeleteUserCommand(user_id=uuid4()))

    assert result.is_err
    assert isinstance(result.error, UserNotFoundError)
    assert not uow.committed


async def test_deactivates_active_user() -> None:
    user = make_user(is_active=True)
    users = FakeUserRepository([user])
    uow = FakeUserUnitOfWork(users)
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    handler = DeleteUserCommandHandler(uow, cache)

    result = await handler.handle(DeleteUserCommand(user_id=user.id))

    assert result.is_ok
    assert users.users[user.id].is_active is False
    assert uow.committed
    assert cache_key(user.id) not in cache.store
