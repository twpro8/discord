from src.modules.auth.domain.entities.dtos import TokenPair
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AuthUnitOfWork,
)
from src.modules.auth.usecases.token_helper import (
    get_valid_refresh_token,
    issue_tokens,
)


class RefreshUseCase:
    def __init__(self, uow: AuthUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, *, refresh_token: str) -> TokenPair:
        stored = await get_valid_refresh_token(self._uow, refresh_token)

        await self._uow.refresh_tokens.revoke(stored.id)
        tokens = await issue_tokens(self._uow, stored.user_id)
        await self._uow.commit()
        return tokens
