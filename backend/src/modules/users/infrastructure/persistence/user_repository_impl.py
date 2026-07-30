import uuid
from dataclasses import asdict

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.entities.dtos import UserCreate, UserUpdate
from src.modules.users.domain.entities.user import User
from src.modules.users.infrastructure.persistence.mappers import (
    model_to_entity,
)
from src.modules.users.infrastructure.persistence.models import UserOrm
from src.shared.domain.unset import set_fields


class UserRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: UserCreate) -> User:
        statement = insert(UserOrm).values(**asdict(data)).returning(UserOrm)
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

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        statement = (
            update(UserOrm)
            .where(UserOrm.id == user_id)
            .values(**set_fields(data))
            .returning(UserOrm)
        )
        result = await self._session.execute(statement)
        return model_to_entity(result.scalar_one())
