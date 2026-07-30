from src.modules.users.application.commands.create_user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from src.modules.users.domain.events.user_registered import UserRegisteredEvent
from src.modules.users.domain.exceptions import InvalidEmail, InvalidUsername
from tests.unit.users.fakes import FakeEventBus, FakeUserRepository, FakeUserUnitOfWork


async def test_rejects_invalid_email() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    handler = CreateUserCommandHandler(uow, FakeEventBus())

    result = await handler.handle(
        CreateUserCommand(
            name="Alice",
            username="alice",
            email="not-an-email",
            plain_password="password123",
        )
    )

    assert result.is_err
    assert isinstance(result.error, InvalidEmail)
    assert not uow.committed


async def test_rejects_invalid_username() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    handler = CreateUserCommandHandler(uow, FakeEventBus())

    result = await handler.handle(
        CreateUserCommand(
            name="Alice",
            username="ab",
            email="alice@example.com",
            plain_password="password123",
        )
    )

    assert result.is_err
    assert isinstance(result.error, InvalidUsername)
    assert not uow.committed


async def test_registers_user_and_publishes_event() -> None:
    users = FakeUserRepository()
    uow = FakeUserUnitOfWork(users)
    event_bus = FakeEventBus()
    handler = CreateUserCommandHandler(uow, event_bus)

    result = await handler.handle(
        CreateUserCommand(
            name="Alice",
            username="alice",
            email="Alice@Example.com",
            plain_password="password123",
        )
    )

    assert result.is_ok
    user = result.value
    assert str(user.email) == "alice@example.com"
    assert str(user.username) == "alice"
    assert users.users[user.id] is user
    assert uow.committed

    assert len(event_bus.published) == 1
    event = event_bus.published[0]
    assert isinstance(event, UserRegisteredEvent)
    assert event.user_id == user.id
    assert event.email == "alice@example.com"
