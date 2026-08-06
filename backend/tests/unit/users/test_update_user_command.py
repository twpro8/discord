from src.modules.users.application.commands.update_user import (
    UpdateUserCommand,
    UpdateUserCommandHandler,
)
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import (
    InvalidEmail,
    InvalidUsername,
    UserAlreadyExistsError,
)
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


async def test_rejects_username_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    uow = FakeUserUnitOfWork(FakeUserRepository([user, other]))
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(username="bob"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, UserAlreadyExistsError)
    assert not uow.committed


async def test_allows_keeping_own_username() -> None:
    user = make_user(username="alice")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(username="alice"),
        )
    )

    assert result.is_ok


async def test_rejects_email_taken_by_another_user() -> None:
    user = make_user(username="alice")
    other = make_user(username="bob")
    uow = FakeUserUnitOfWork(FakeUserRepository([user, other]))
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(email="bob@test.com"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, UserAlreadyExistsError)


async def test_rejects_invalid_username_value() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(username="ab"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, InvalidUsername)


async def test_rejects_invalid_email_value() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    handler = UpdateUserCommandHandler(uow, FakeCache())

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(email="not-an-email"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, InvalidEmail)
