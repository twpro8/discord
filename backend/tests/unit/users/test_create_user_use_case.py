from src.modules.users.usecases.create_user import CreateUserUseCase
from tests.unit.users.fakes import FakeUserRepository


async def test_registers_user() -> None:
    users = FakeUserRepository()
    use_case = CreateUserUseCase(users)

    user = await use_case(
        name="Alice",
        username="alice",
        email="Alice@Example.com",
        plain_password="password123",
    )

    assert user.email == "alice@example.com"
    assert user.username == "alice"
    assert users.users[user.id] is user
