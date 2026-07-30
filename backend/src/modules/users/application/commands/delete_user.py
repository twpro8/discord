from dataclasses import dataclass
from uuid import UUID

from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class DeleteUserCommand(Command):
    user_id: UUID


class DeleteUserCommandHandler:
    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DeleteUserCommand) -> Result[None, LumiereError]:
        user = await self._uow.users.get_by_id(command.user_id)
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())

        user.mark_as_inactive()
        await self._uow.users.update(user.id, UserUpdate(is_active=False))
        await self._uow.commit()
        return Result.ok(None)
