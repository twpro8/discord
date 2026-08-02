"""Integration tests for the realtime WebSocket fan-out."""

from collections.abc import AsyncIterator, Iterator
from uuid import UUID

import pytest
from fakeredis.aioredis import FakeRedis
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.api.v1.dependencies import get_pubsub, get_redis
from src.core.realtime.notifier import RedisRealtimeNotifier, user_topic
from src.core.realtime.redis_pubsub import RedisPubSubTransport
from src.main import app

ALICE_USERNAME = "alice"
BOB_USERNAME = "monica"
PASSWORD = "12345678"

ALICE_ID = UUID("a2b3c4d5-e6f7-4a5b-8c9d-0e1f2a3b4c5d")
BOB_ID = UUID("1df5569d-c4bf-488e-9f0f-30946a7067c9")


@pytest.fixture
def fake_redis() -> Iterator[FakeRedis]:
    redis = FakeRedis(decode_responses=True)
    previous_redis = app.dependency_overrides.get(get_redis)
    previous_pubsub = app.dependency_overrides.get(get_pubsub)
    app.dependency_overrides[get_redis] = lambda: redis
    app.dependency_overrides[get_pubsub] = lambda: RedisPubSubTransport(redis)
    yield redis
    if previous_redis is not None:
        app.dependency_overrides[get_redis] = previous_redis
    else:
        app.dependency_overrides.pop(get_redis, None)
    if previous_pubsub is not None:
        app.dependency_overrides[get_pubsub] = previous_pubsub
    else:
        app.dependency_overrides.pop(get_pubsub, None)


@pytest.fixture
def client(
    fake_redis: FakeRedis, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    # lifespan binds these by name in src.main, so patch them there.
    async def fake_init() -> FakeRedis:
        return fake_redis

    async def fake_close(_redis: object) -> None:
        return None

    monkeypatch.setattr("src.main.init_redis", fake_init)
    monkeypatch.setattr("src.main.close_redis", fake_close)

    with TestClient(app) as test_client:
        yield test_client


def _login(client: TestClient, username: str) -> str:
    client.cookies.clear()
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200
    token = client.cookies.get("access_token")
    assert token
    return token


def _set_access_token(client: TestClient, token: str) -> None:
    client.cookies.delete("access_token")
    client.cookies.set("access_token", token)


class RecordingTransport:
    def __init__(self) -> None:
        self.published: list[tuple[str, str]] = []

    async def publish(self, topic: str, payload: str) -> None:
        self.published.append((topic, payload))

    async def subscribe(self, topic: str) -> AsyncIterator[str]:
        if False:  # pragma: no cover - never used by the notifier
            yield topic


async def test_notifier_publishes_to_user_topic() -> None:
    transport = RecordingTransport()
    notifier = RedisRealtimeNotifier(transport)

    await notifier.publish_user_event(ALICE_ID, {"type": "message.created"})

    assert transport.published == [
        (user_topic(ALICE_ID), '{"type": "message.created"}')
    ]


def test_websocket_requires_auth(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/ws"):
            pass
    assert exc_info.value.code == 4401


def test_message_fans_out_to_members(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _login(client, ALICE_USERNAME)
            chat_resp = client.post(
                "/api/v1/chats",
                json={"type": "private", "target_user_id": str(BOB_ID)},
            )
            assert chat_resp.status_code == 201
            chat_id = chat_resp.json()["id"]

            message_resp = client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"body": "hello over the wire"},
            )
            assert message_resp.status_code == 200

            for ws in (alice_ws, bob_ws):
                event = ws.receive_json()
                assert event["type"] == "message.created"
                payload = event["payload"]
                assert payload["body"] == "hello over the wire"
                assert payload["chat_id"] == chat_id
                assert payload["sender_id"] == str(ALICE_ID)
