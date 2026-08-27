import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.domain.entities.user import User
from src.modules.users.adapters.persistence.mappers import UserDataMapper
from src.modules.users.adapters.persistence.models import UserOrm
from tests.data import users


@pytest.fixture
async def current_user(session: AsyncSession) -> User:
    user = users[0]
    query = select(UserOrm).filter_by(id=user["id"])
    result = await session.scalars(query)
    return UserDataMapper.to_entity(result.one())


@pytest.fixture
async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(UserOrm))
    models = result.scalars().all()
    return [UserDataMapper.to_entity(model) for model in models]
