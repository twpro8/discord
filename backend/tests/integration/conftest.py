import subprocess
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_null_pool_session_factory
from tests.seeder import populate_database


@pytest.fixture(scope="session", autouse=True)
async def setup_database(
    check_test_mode: None,  # noqa
) -> None:
    """Setup database tables"""
    subprocess.run(
        ["alembic", "downgrade", "base"],
        check=True,
    )
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
async def populated_database(
    setup_database: None,  # noqa
) -> AsyncGenerator[AsyncSession]:
    """Populate database"""
    session_factory = get_null_pool_session_factory()
    async with session_factory() as session:
        await populate_database(session)
        yield session
