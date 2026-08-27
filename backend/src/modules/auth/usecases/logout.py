from src.modules.auth.domain.exceptions import InvalidRefreshTokenError
from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.modules.auth.usecases.token_helper import get_valid_refresh_token
from src.shared.domain.transaction import Transaction


class LogoutUseCase:
    def __init__(
        self, tx: Transaction, refresh_token_repository: RefreshTokenRepository
    ) -> None:
        # tx isn't committed here directly (this use case's own write is the
        # last thing that happens, so the request's auto-commit covers it)
        # — it's forwarded to get_valid_refresh_token, which needs it for
        # its own commit-before-raise branch.
        self._tx = tx
        self._refresh_tokens = refresh_token_repository

    async def __call__(self, *, refresh_token: str) -> None:
        try:
            stored = await get_valid_refresh_token(
                self._tx, self._refresh_tokens, refresh_token
            )
        except InvalidRefreshTokenError:
            return
        await self._refresh_tokens.revoke(stored.id)
