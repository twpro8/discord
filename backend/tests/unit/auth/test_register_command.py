from src.modules.auth.application.commands.register import (
    RegisterCommand,
    RegisterCommandHandler,
)
from src.modules.auth.domain.entities.dtos import RegisterData
from tests.unit.auth.fakes import FakeUsersFacade


async def test_creates_user_with_hashed_password() -> None:
    users_facade = FakeUsersFacade()
    handler = RegisterCommandHandler(users_facade)

    result = await handler.handle(
        RegisterCommand(
            data=RegisterData(
                name="Alice",
                username="alice",
                email="alice@test.com",
                password="12345678",
            )
        )
    )

    assert result.is_ok
    user = result.value
    assert user.username == "alice"
    assert users_facade.users[user.id].password_hash != "12345678"
