from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.postgres.engine import engine, null_pool_engine

session_maker = async_sessionmaker(engine, expire_on_commit=False)
null_pool_session_maker = async_sessionmaker(
    bind=null_pool_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session
