from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.domain.schemas import RefreshTokenCreate
from src.modules.auth.infrastructure.persistence.mappers import model_to_entity
from src.modules.auth.infrastructure.persistence.models import RefreshTokenOrm


class RefreshTokenRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: RefreshTokenCreate) -> RefreshToken:
        stmt = (
            insert(RefreshTokenOrm)
            .values(**data.model_dump())
            .returning(RefreshTokenOrm)
        )
        result = await self._session.execute(stmt)
        return model_to_entity(result.scalar_one())

    async def find_by_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(RefreshTokenOrm).filter_by(token_hash=token_hash)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return model_to_entity(model) if model else None

    async def revoke(self, token_id: UUID) -> None:
        stmt = (
            update(RefreshTokenOrm)
            .filter_by(id=token_id, is_revoked=False)
            .values({"is_revoked": True})
        )
        await self._session.execute(stmt)

    async def revoke_all(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshTokenOrm)
            .filter_by(user_id=user_id, is_revoked=False)
            .values({"is_revoked": True})
        )
        await self._session.execute(stmt)
