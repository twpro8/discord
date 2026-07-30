from uuid import UUID

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import (
    AbstractUserUnitOfWork,
)
from src.modules.users.transport.http.schemas import UserUpdateRequest
from src.shared.errors import LumiereError
from src.shared.result import Result


class UpdateUserCommand:
    def __init__(self, uow: AbstractUserUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, user_id: UUID, data: UserUpdateRequest
    ) -> Result[User, LumiereError]:
        user = await self._uow.users.update(user_id, data, exclude_unset=True)
        await self._uow.commit()
        return Result.ok(user)
