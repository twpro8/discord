from dataclasses import dataclass

from src.core.security.hashing import verify_password
from src.modules.auth.application.token_helper import issue_tokens
from src.modules.auth.domain.entities.schemas import TokenPair
from src.modules.auth.domain.exceptions import IncorrectPasswordError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.users.domain.exceptions import UserNotFoundError
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class LoginCommand(Command):
    username: str
    password: str


class LoginCommandHandler:
    def __init__(self, uow: AbstractAuthUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: LoginCommand) -> Result[TokenPair, LumiereError]:
        user = await self._uow.users.get_by_username(command.username)
        if not user or not user.is_active:
            return Result.err(UserNotFoundError())
        if not verify_password(command.password, user.password_hash):
            return Result.err(IncorrectPasswordError())
        tokens = await issue_tokens(self._uow, user.id)
        await self._uow.commit()
        return Result.ok(tokens)
