from src.modules.users.application.commands.update_user import (
    UpdateUserCommand,
    UpdateUserCommandHandler,
)
from src.modules.users.domain.entities.dtos import UserUpdate
from tests.unit.users.fakes import FakeUserRepository, FakeUserUnitOfWork, make_user


async def test_partial_update_only_touches_provided_fields() -> None:
    user = make_user(username="original")
    users = FakeUserRepository([user])
    uow = FakeUserUnitOfWork(users)
    handler = UpdateUserCommandHandler(uow)

    result = await handler.handle(
        UpdateUserCommand(
            user_id=user.id,
            data=UserUpdate(name="New Name"),
        )
    )

    assert result.is_ok
    updated = result.value
    assert updated.name == "New Name"
    assert updated.username == "original"
    assert uow.committed
