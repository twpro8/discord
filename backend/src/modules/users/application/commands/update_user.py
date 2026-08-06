from dataclasses import dataclass
from uuid import UUID

from src.core.cache import Cache
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.exceptions import UserAlreadyExistsError, UserError
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.shared.application.command import Command
from src.shared.domain.unset import set_fields
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class UpdateUserCommand(Command):
    user_id: UUID
    data: UserUpdate


class UpdateUserCommandHandler:
    def __init__(self, uow: UserUnitOfWork, cache: Cache) -> None:
        self._uow = uow
        self._cache = cache

    async def handle(self, command: UpdateUserCommand) -> Result[UserDTO, LumiereError]:
        updates = set_fields(command.data)
        try:
            if "username" in updates:
                username = Username(updates["username"])
            if "email" in updates:
                email = Email(updates["email"])
        except UserError as error:
            return Result.err(error)

        if "username" in updates:
            existing = await self._uow.users.get_by_username(str(username))
            if existing is not None and existing.id != command.user_id:
                return Result.err(UserAlreadyExistsError())
        if "email" in updates:
            existing = await self._uow.users.get_by_email(str(email))
            if existing is not None and existing.id != command.user_id:
                return Result.err(UserAlreadyExistsError())

        user = await self._uow.users.update(command.user_id, command.data)
        await self._uow.commit()
        await self._cache.delete(cache_key(command.user_id))
        return Result.ok(user_to_dto(user))
