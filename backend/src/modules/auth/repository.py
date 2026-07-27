from uuid import UUID

from sqlalchemy import update

from src.common.repositories import BaseRepository
from src.modules.auth.mappers import AuthMapper
from src.modules.auth.models import RefreshTokenOrm
from src.modules.auth.schemas import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshTokenOrm, RefreshToken]):
    model = RefreshTokenOrm
    mapper = AuthMapper

    async def revoke(self, token_id: UUID) -> None:
        statement = (
            update(RefreshTokenOrm)
            .filter_by(id=token_id)
            .values(
                {
                    "is_revoked": True,
                }
            )
        )
        await self.session.execute(statement)

    async def revoke_all(self, user_id: UUID) -> None:
        statement = (
            update(RefreshTokenOrm)
            .filter_by(user_id=user_id, is_revoked=False)
            .values(
                {
                    "is_revoked": True,
                }
            )
        )
        await self.session.execute(statement)
