from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_null_pool_session_factory


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    session_factory = get_null_pool_session_factory()
    async with session_factory() as session:
        yield session
