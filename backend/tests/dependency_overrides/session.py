from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.postgres.session import null_pool_session_maker


async def get_null_pool_session() -> AsyncGenerator[AsyncSession]:
    async with null_pool_session_maker() as null_pool_session:
        yield null_pool_session
