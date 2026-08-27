from src.modules.auth.domain.entities.dtos import TokenPair
from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.modules.auth.usecases.token_helper import (
    get_valid_refresh_token,
    issue_tokens,
)
from src.shared.domain.transaction import Transaction


class RefreshUseCase:
    def __init__(
        self, tx: Transaction, refresh_token_repository: RefreshTokenRepository
    ) -> None:
        # See LogoutUseCase — tx is forwarded to get_valid_refresh_token for
        # its commit-before-raise branch; this use case's own writes are
        # last, so the request's auto-commit covers them.
        self._tx = tx
        self._refresh_tokens = refresh_token_repository

    async def __call__(self, *, refresh_token: str) -> TokenPair:
        stored = await get_valid_refresh_token(
            self._tx, self._refresh_tokens, refresh_token
        )

        await self._refresh_tokens.revoke(stored.id)
        return await issue_tokens(self._refresh_tokens, stored.user_id)
