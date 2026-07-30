from dataclasses import dataclass

from src.modules.auth.application.token_helper import issue_tokens
from src.modules.auth.domain.entities.dtos import TokenPair
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class LoginCommand(Command):
    username: str
    password: str


class LoginCommandHandler:
    def __init__(self, uow: AbstractAuthUnitOfWork, users_facade: UsersFacade) -> None:
        self._uow = uow
        self._users_facade = users_facade

    async def handle(self, command: LoginCommand) -> Result[TokenPair, LumiereError]:
        result = await self._users_facade.verify_credentials(
            username=command.username,
            plain_password=command.password,
        )
        if result.is_err:
            return Result.err(result.error)

        tokens = await issue_tokens(self._uow, result.value.id)
        await self._uow.commit()
        return Result.ok(tokens)
