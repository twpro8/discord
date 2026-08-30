from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.core.database import get_session
from src.main import app
from src.modules.users.domain.entities.user import User
from src.core.database.models import *  # noqa
from tests.dependency_overrides.cache import get_test_cache
from tests.dependency_overrides.job_dispatcher import get_test_job_dispatcher
from tests.dependency_overrides.redis_client import get_fake_redis_client
from tests.dependency_overrides.redis_subscription_manager import (
    get_test_redis_subscription_manager,
)
from tests.dependency_overrides.session import get_null_pool_session
from tests.dependency_overrides.storage import get_test_storage


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> None:
    """Ensure test mode is enabled"""
    assert settings.ENVIRONMENT == "testing"


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(
    check_test_mode: None,  # noqa
) -> None:
    """Override dependencies once for all tests"""
    from src.api.v1.dependencies import (
        get_cache,
        get_job_dispatcher,
        get_redis,
        get_redis_subscription_manager,
        get_storage,
    )

    app.dependency_overrides[get_session] = get_null_pool_session
    app.dependency_overrides[get_redis] = get_fake_redis_client
    app.dependency_overrides[get_cache] = get_test_cache
    app.dependency_overrides[get_redis_subscription_manager] = (
        get_test_redis_subscription_manager
    )
    app.dependency_overrides[get_job_dispatcher] = get_test_job_dispatcher
    app.dependency_overrides[get_storage] = get_test_storage


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
    "tests.fixtures.users",
]
