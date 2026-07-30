from dataclasses import dataclass
from uuid import UUID

from src.core.cache import Cache
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.shared.application.command import Command
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
        user = await self._uow.users.update(command.user_id, command.data)
        await self._uow.commit()
        await self._cache.delete(cache_key(command.user_id))
        return Result.ok(user_to_dto(user))
