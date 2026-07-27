from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.platform.config import settings


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(str(settings.DATABASE_URL))


@lru_cache
def get_null_pool_engine() -> AsyncEngine:
    return create_async_engine(str(settings.DATABASE_URL), poolclass=NullPool)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        autoflush=False,
    )


@lru_cache
def get_null_pool_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_null_pool_engine(), expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
