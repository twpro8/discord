from src.modules.auth.domain.entities.dtos import RegisterData
from src.modules.auth.usecases.register import RegisterUseCase
from tests.unit.auth.fakes import FakeUsersFacade


async def test_creates_user_with_hashed_password() -> None:
    users_facade = FakeUsersFacade()
    use_case = RegisterUseCase(users_facade)

    user = await use_case(
        data=RegisterData(
            name="Alice",
            username="alice",
            email="alice@test.com",
            password="12345678",
        )
    )

    assert user.username == "alice"
    assert users_facade.users[user.id].password_hash != "12345678"
