from src.modules.auth.application.token_helper import get_valid_refresh_token
from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class LogoutCommand:
    def __init__(self, uow: AbstractAuthUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, refresh_token: str) -> Result[None, LumiereError]:
        try:
            stored = await get_valid_refresh_token(self._uow, refresh_token)
        except InvalidRefreshTokenError:
            return Result.ok(None)
        await self._uow.refresh_tokens.revoke(stored.id)
        await self._uow.commit()
        return Result.ok(None)
