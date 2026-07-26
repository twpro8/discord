import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.user.models import UserOrm
from src.modules.user.schemas import User
from tests.data import users


@pytest.fixture
async def current_user(session: AsyncSession) -> User:
    user = users[0]
    query = select(UserOrm).filter_by(id=user["id"])
    result = await session.scalars(query)
    return User.model_validate(result.one())


@pytest.fixture
async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(UserOrm))
    models = result.scalars().all()
    return [User.model_validate(model) for model in models]
