from dataclasses import dataclass
from uuid import UUID

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.modules.users.transport.http.schemas import UserUpdateRequest
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class UpdateUserCommand(Command):
    user_id: UUID
    data: UserUpdateRequest


class UpdateUserCommandHandler:
    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UpdateUserCommand) -> Result[User, LumiereError]:
        user = await self._uow.users.update(
            command.user_id, command.data, exclude_unset=True
        )
        await self._uow.commit()
        return Result.ok(user)
