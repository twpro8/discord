from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.core.database import get_session
from src.core.database.session import get_null_pool_session_factory
from src.main import app
from src.modules.users.domain.entities.user import User
from src.shared.data.models import *  # noqa
from tests.dependency_overrides.cache import get_test_cache
from tests.dependency_overrides.event_bus import get_test_event_bus
from tests.dependency_overrides.redis_client import get_fake_redis_client
from tests.dependency_overrides.redis_subscription_manager import (
    get_test_redis_subscription_manager,
)
from tests.dependency_overrides.session import get_null_pool_session


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
        get_event_bus,
        get_redis,
        get_redis_subscription_manager,
    )
    from src.api.v1.ws import get_session_factory_ws

    app.dependency_overrides[get_session] = get_null_pool_session
    app.dependency_overrides[get_redis] = get_fake_redis_client
    app.dependency_overrides[get_event_bus] = get_test_event_bus
    app.dependency_overrides[get_cache] = get_test_cache
    app.dependency_overrides[get_redis_subscription_manager] = (
        get_test_redis_subscription_manager
    )
    app.dependency_overrides[get_session_factory_ws] = get_null_pool_session_factory


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
            "username": str(current_user.username),
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
