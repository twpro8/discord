from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.postgres.session import null_pool_session_maker


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    async with null_pool_session_maker() as session:
        yield session
