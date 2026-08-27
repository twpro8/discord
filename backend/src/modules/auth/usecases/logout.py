from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AuthUnitOfWork,
)
from src.modules.auth.usecases.token_helper import get_valid_refresh_token


class LogoutUseCase:
    def __init__(self, uow: AuthUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, *, refresh_token: str) -> None:
        try:
            stored = await get_valid_refresh_token(self._uow, refresh_token)
        except InvalidRefreshTokenError:
            return
        await self._uow.refresh_tokens.revoke(stored.id)
        await self._uow.commit()
