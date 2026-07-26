from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.database.session import get_null_pool_session_factory


async def get_null_pool_session() -> AsyncGenerator[AsyncSession]:
    session_factory = get_null_pool_session_factory()
    async with session_factory() as null_pool_session:
        yield null_pool_session
