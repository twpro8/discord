from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.modules.users.domain.schemas import User
from src.platform.config import settings
from src.platform.database import Base, get_session
from src.platform.database.session import (
    get_null_pool_engine,
    get_null_pool_session_factory,
)
from src.shared.models import *  # noqa
from tests.dependency_overrides.redis_client import get_fake_redis_client
from tests.dependency_overrides.session import get_null_pool_session
from tests.seeder import populate_database


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> None:
    """Ensure test mode is enabled"""
    assert settings.ENVIRONMENT == "testing"


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(
    check_test_mode: None,  # noqa
) -> None:
    """Override dependencies once for all tests"""
    from src.api.v1.dependencies import get_redis

    app.dependency_overrides[get_session] = get_null_pool_session
    app.dependency_overrides[get_redis] = get_fake_redis_client


@pytest.fixture(scope="session", autouse=True)
async def setup_database(
    check_test_mode: None,  # noqa
) -> None:
    """Setup database tables"""
    engine = get_null_pool_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def populated_database(
    setup_database: None,  # noqa
) -> AsyncGenerator[AsyncSession]:
    """Populate database"""
    session_factory = get_null_pool_session_factory()
    async with session_factory() as session:
        await populate_database(session)
        yield session


@pytest.fixture(name="ac")
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    """Async client fixture"""
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture
async def authed_client(
    ac: AsyncClient,
    current_user: User,
) -> AsyncGenerator[AsyncClient, Any]:
    """Authenticated async http client fixture"""
    response = await ac.post(
        "/api/v1/auth/login",
        json={
            "username": current_user.username,
            "password": "12345678",
        },
    )
    assert response.status_code == 200
    assert ac.cookies.get("access_token")
    assert ac.cookies.get("refresh_token")
    yield ac


pytest_plugins = [
    "tests.fixtures.session",
    "tests.fixtures.user",
]
