from dataclasses import dataclass
from uuid import UUID

from src.core.cache import Cache
from src.core.security.hashing import hash_password, verify_password
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class ChangePasswordCommand(Command):
    user_id: UUID
    current_password: str
    new_password: str


class ChangePasswordCommandHandler:
    def __init__(self, uow: UserUnitOfWork, cache: Cache) -> None:
        self._uow = uow
        self._cache = cache

    async def handle(
        self, command: ChangePasswordCommand
    ) -> Result[None, LumiereError]:
        user = await self._uow.users.get_by_id(command.user_id)
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())
        if not verify_password(command.current_password, user.password_hash):
            return Result.err(IncorrectPasswordError())

        await self._uow.users.update(
            command.user_id,
            UserUpdate(password_hash=hash_password(command.new_password)),
        )
        await self._uow.commit()
        await self._cache.delete(cache_key(command.user_id))
        return Result.ok(None)
