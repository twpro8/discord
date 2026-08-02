from functools import lru_cache

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings


def get_engine() -> AsyncEngine:
    """Build a new production database engine.

    Not cached: built exactly once per process, either by prestart.py's
    standalone migration-readiness check or by main.py's lifespan (which
    stores the result on app.state, mirroring how the Redis pool is
    managed, and disposes of it on shutdown).
    """
    return create_async_engine(str(settings.DATABASE_URL))


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@lru_cache
def get_null_pool_engine() -> AsyncEngine:
    return create_async_engine(str(settings.DATABASE_URL), poolclass=NullPool)


@lru_cache
def get_null_pool_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_null_pool_engine(), expire_on_commit=False)
