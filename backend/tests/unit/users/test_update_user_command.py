from src.modules.users.application.commands.update_user import (
    UpdateUserCommand,
    UpdateUserCommandHandler,
)
from src.modules.users.transport.http.schemas import UserUpdateRequest
from tests.unit.users.fakes import FakeUserRepository, FakeUserUnitOfWork, make_user


async def test_partial_update_only_touches_provided_fields() -> None:
    user = make_user(username="original")
    users = FakeUserRepository([user])
    uow = FakeUserUnitOfWork(users)
    handler = UpdateUserCommandHandler(uow)

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdateRequest(name="New Name"),  # type: ignore[call-arg]
        )
    )

    assert result.is_ok
    updated = result.value
    assert updated.name == "New Name"
    assert updated.username == "original"
    assert uow.committed
