"""Shared fixtures for presence integration tests — mirrors
tests/integration/realtime/test_ws.py's `client` fixture, with two
additions: `get_redis` is also un-overridden, and `get_session_factory` is
patched to the null-pool variant.

conftest.py's global `override_dependencies` fixture points `get_redis` at
`get_fake_redis_client`, which returns a *fresh, disconnected*
`FakeRedis()` (no `decode_responses=True`) on every call — harmless before
this feature since nothing consumed `RedisDep` directly, but presence's
`GET /presence/*` query handlers are its first real consumer. Without
un-overriding it here, the REST endpoints would read from a different,
empty, bytes-mode Redis than the one PresenceService (built from the real
`app.state.redis`, set up via the monkeypatched `init_redis` below) writes
to over the WebSocket.

Separately: PresenceService opens its own DB sessions (for the friend/
server lookups on a transition) directly via `get_session_factory()` in
main.py's lifespan closure, not through the `get_session` FastAPI
dependency — so the global `get_session` -> `get_null_pool_session`
override (tests/dependency_overrides/session.py) never applies to it.
Patched the same way `init_redis`/`close_redis` are patched below.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID

import pytest
from fakeredis.aioredis import FakeRedis
from starlette.testclient import TestClient

from src.api.v1.dependencies import get_redis, get_redis_subscription_manager
from src.core.database.session import get_null_pool_session_factory
from src.main import app

ALICE_USERNAME = "alice"
BOB_USERNAME = "monica"
PASSWORD = "12345678"

ALICE_ID = UUID("a2b3c4d5-e6f7-4a5b-8c9d-0e1f2a3b4c5d")
BOB_ID = UUID("1df5569d-c4bf-488e-9f0f-30946a7067c9")


@contextmanager
def _without_override(dependency: Callable[..., object]) -> Iterator[None]:
    previous = app.dependency_overrides.pop(dependency, None)
    try:
        yield
    finally:
        if previous is not None:
            app.dependency_overrides[dependency] = previous


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    async def fake_init() -> FakeRedis:
        return FakeRedis(decode_responses=True)

    async def fake_close(_redis: object) -> None:
        return None

    monkeypatch.setattr("src.main.init_redis", fake_init)
    monkeypatch.setattr("src.main.close_redis", fake_close)
    monkeypatch.setattr("src.main.get_session_factory", get_null_pool_session_factory)

    with (
        _without_override(get_redis_subscription_manager),
        _without_override(get_redis),
        TestClient(app) as test_client,
    ):
        yield test_client


def login(client: TestClient, username: str) -> str:
    client.cookies.clear()
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200
    token = client.cookies.get("access_token")
    assert token
    return token


def set_access_token(client: TestClient, token: str) -> None:
    client.cookies.delete("access_token")
    client.cookies.set("access_token", token)
