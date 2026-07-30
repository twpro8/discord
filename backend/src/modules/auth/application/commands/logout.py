from dataclasses import dataclass

from src.modules.auth.application.token_helper import get_valid_refresh_token
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AuthUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class LogoutCommand(Command):
    refresh_token: str


class LogoutCommandHandler:
    def __init__(self, uow: AuthUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: LogoutCommand) -> Result[None, LumiereError]:
        try:
            stored = await get_valid_refresh_token(self._uow, command.refresh_token)
        except InvalidRefreshTokenError:
            return Result.ok(None)
        await self._uow.refresh_tokens.revoke(stored.id)
        await self._uow.commit()
        return Result.ok(None)
