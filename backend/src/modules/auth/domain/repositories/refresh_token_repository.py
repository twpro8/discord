from typing import Protocol
from uuid import UUID

from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.entities.schemas import RefreshTokenCreate


class RefreshTokenRepository(Protocol):
    async def create(self, data: RefreshTokenCreate) -> RefreshToken: ...

    async def find_by_hash(self, token_hash: str) -> RefreshToken | None: ...

    async def revoke(self, token_id: UUID) -> None: ...

    async def revoke_all(self, user_id: UUID) -> None: ...
