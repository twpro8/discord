from src.core.security.hashing import verify_password
from src.modules.auth.application.commands.register import (
    RegisterCommand,
    RegisterCommandHandler,
)
from src.modules.auth.domain.entities.schemas import RegisterForm
from tests.unit.auth.fakes import (
    FakeAuthUnitOfWork,
    FakeRefreshTokenRepository,
    FakeUserRepository,
)


async def test_creates_user_with_hashed_password() -> None:
    users = FakeUserRepository()
    uow = FakeAuthUnitOfWork(users, FakeRefreshTokenRepository())
    handler = RegisterCommandHandler(uow)

    result = await handler.handle(
        RegisterCommand(
            form_data=RegisterForm(
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
    assert user.password_hash != "12345678"
    assert verify_password("12345678", user.password_hash)
    assert uow.committed
