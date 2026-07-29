from dataclasses import dataclass

from src.modules.auth.application.token_helper import (
    get_valid_refresh_token,
    issue_tokens,
)
from src.modules.auth.domain.entities.schemas import TokenPair
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class RefreshCommand(Command):
    refresh_token: str


class RefreshCommandHandler:
    def __init__(self, uow: AbstractAuthUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: RefreshCommand
    ) -> Result[TokenPair, InvalidRefreshTokenError]:
        try:
            stored = await get_valid_refresh_token(self._uow, command.refresh_token)
        except InvalidRefreshTokenError as error:
            return Result.err(error)

        await self._uow.refresh_tokens.revoke(stored.id)
        tokens = await issue_tokens(self._uow, stored.user_id)
        await self._uow.commit()
        return Result.ok(tokens)
