import uuid

from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.entities.user import User
from src.modules.users.infrastructure.persistence.mappers import (
    model_to_entity,
)
from src.modules.users.infrastructure.persistence.models import UserOrm


class UserRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: BaseModel) -> User:
        statement = insert(UserOrm).values(**data.model_dump()).returning(UserOrm)
        result = await self._session.execute(statement)
        return model_to_entity(result.scalar_one())

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        query = select(UserOrm).where(UserOrm.id == user_id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        query = select(UserOrm).filter_by(username=username)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return model_to_entity(model) if model else None

    async def update(
        self,
        user_id: uuid.UUID,
        data: BaseModel,
        exclude_unset: bool = False,
    ) -> User:
        statement = (
            update(UserOrm)
            .where(UserOrm.id == user_id)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(UserOrm)
        )
        result = await self._session.execute(statement)
        return model_to_entity(result.scalar_one())
