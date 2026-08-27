import pytest

from src.modules.users.domain.events.user_registered import UserRegisteredEvent
from src.modules.users.domain.exceptions import InvalidEmail, InvalidUsername
from src.modules.users.usecases.create_user import CreateUserUseCase
from tests.unit.fakes import FakeTransaction
from tests.unit.users.fakes import FakeEventBus, FakeUserRepository


async def test_rejects_invalid_email() -> None:
    tx = FakeTransaction()
    use_case = CreateUserUseCase(tx, FakeUserRepository(), FakeEventBus())

    with pytest.raises(InvalidEmail):
        await use_case(
            name="Alice",
            username="alice",
            email="not-an-email",
            plain_password="password123",
        )

    assert not tx.committed


async def test_rejects_invalid_username() -> None:
    tx = FakeTransaction()
    use_case = CreateUserUseCase(tx, FakeUserRepository(), FakeEventBus())

    with pytest.raises(InvalidUsername):
        await use_case(
            name="Alice",
            username="ab",
            email="alice@example.com",
            plain_password="password123",
        )

    assert not tx.committed


async def test_registers_user_and_publishes_event() -> None:
    users = FakeUserRepository()
    tx = FakeTransaction()
    event_bus = FakeEventBus()
    use_case = CreateUserUseCase(tx, users, event_bus)

    user = await use_case(
        name="Alice",
        username="alice",
        email="Alice@Example.com",
        plain_password="password123",
    )

    assert str(user.email) == "alice@example.com"
    assert str(user.username) == "alice"
    assert users.users[user.id] is user
    assert tx.committed

    assert len(event_bus.published) == 1
    event = event_bus.published[0]
    assert isinstance(event, UserRegisteredEvent)
    assert event.user_id == user.id
    assert event.email == "alice@example.com"
