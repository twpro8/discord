import pytest

from src.modules.users.domain.events.user_registered import UserRegisteredEvent
from src.modules.users.domain.exceptions import InvalidEmail, InvalidUsername
from src.modules.users.usecases.create_user import CreateUserUseCase
from tests.unit.users.fakes import FakeEventBus, FakeUserRepository, FakeUserUnitOfWork


async def test_rejects_invalid_email() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    use_case = CreateUserUseCase(uow, FakeEventBus())

    with pytest.raises(InvalidEmail):
        await use_case(
            name="Alice",
            username="alice",
            email="not-an-email",
            plain_password="password123",
        )

    assert not uow.committed


async def test_rejects_invalid_username() -> None:
    uow = FakeUserUnitOfWork(FakeUserRepository())
    use_case = CreateUserUseCase(uow, FakeEventBus())

    with pytest.raises(InvalidUsername):
        await use_case(
            name="Alice",
            username="ab",
            email="alice@example.com",
            plain_password="password123",
        )

    assert not uow.committed


async def test_registers_user_and_publishes_event() -> None:
    users = FakeUserRepository()
    uow = FakeUserUnitOfWork(users)
    event_bus = FakeEventBus()
    use_case = CreateUserUseCase(uow, event_bus)

    user = await use_case(
        name="Alice",
        username="alice",
        email="Alice@Example.com",
        plain_password="password123",
    )

    assert str(user.email) == "alice@example.com"
    assert str(user.username) == "alice"
    assert users.users[user.id] is user
    assert uow.committed

    assert len(event_bus.published) == 1
    event = event_bus.published[0]
    assert isinstance(event, UserRegisteredEvent)
    assert event.user_id == user.id
    assert event.email == "alice@example.com"
