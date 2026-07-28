from typing import Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.auth.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    async def create(self, data: BaseModel) -> RefreshToken: ...

    async def get_one(self, **kwargs: object) -> RefreshToken | None: ...

    async def revoke(self, token_id: UUID) -> None: ...

    async def revoke_all(self, user_id: UUID) -> None: ...
