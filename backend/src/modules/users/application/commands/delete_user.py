from src.modules.users.domain.entities.schemas import UserDeactivate
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import (
    AbstractUserUnitOfWork,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class DeleteUserCommand:
    def __init__(self, uow: AbstractUserUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, user: User) -> Result[None, LumiereError]:
        user.mark_as_inactive()
        await self._uow.users.update(user.id, UserDeactivate())
        await self._uow.commit()
        return Result.ok(None)
