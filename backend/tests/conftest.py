from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.models import *  # noqa
from src.core.postgres import Base, get_session
from src.core.postgres.engine import null_pool_engine
from src.core.postgres.session import null_pool_session_maker
from src.main import app
from src.user.schemas import User
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
    from src.core.dependencies import get_redis

    app.dependency_overrides[get_session] = get_null_pool_session
    app.dependency_overrides[get_redis] = get_fake_redis_client


@pytest.fixture(scope="session", autouse=True)
async def setup_database(
    check_test_mode: None,  # noqa
) -> None:
    """Setup database tables"""
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def populated_database(
    setup_database: None,  # noqa
) -> AsyncGenerator[AsyncSession]:
    """Populate database"""
    async with null_pool_session_maker() as session:
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
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": current_user.username,
            "password": "12345678",
        },
    )
    assert response.status_code == 200

    auth_result = response.json()

    access_token = auth_result.get("access_token")
    refresh_token = auth_result.get("refresh_token")

    assert access_token, "No access token in response body"
    assert refresh_token, "No refresh token in response body"

    ac.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
        }
    )

    yield ac


pytest_plugins = [
    "tests.fixtures.session",
    "tests.fixtures.user",
]
