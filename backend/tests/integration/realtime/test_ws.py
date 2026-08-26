"""Integration tests for the realtime WebSocket fan-out.

Message delivery goes through RedisRealtimeNotifier -> chat_room(chat_id)
(see api/v1/dependencies.py::get_realtime_notifier); room membership itself is
kept current by DistributedRoomMembershipUpdater, published to
user_room(user_id) so every instance with a local connection for that
user — including this one — picks it up the same way (see
core.realtime.membership). Both round-trip through Redis even for this
single "instance" under test.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID

import pytest
from fakeredis.aioredis import FakeRedis
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.api.v1.dependencies import get_redis_subscription_manager
from src.main import app

ALICE_USERNAME = "alice"
BOB_USERNAME = "monica"
PASSWORD = "12345678"

ALICE_ID = UUID("a2b3c4d5-e6f7-4a5b-8c9d-0e1f2a3b4c5d")
BOB_ID = UUID("1df5569d-c4bf-488e-9f0f-30946a7067c9")


@contextmanager
def _without_override(dependency: Callable[..., object]) -> Iterator[None]:
    """conftest.py's global override hands get_realtime_notifier/
    get_room_membership_updater a fresh, throwaway RedisSubscriptionManager
    per call — fine for tests that only need those to resolve, but these
    tests need the single real instance the lifespan creates on
    app.state, shared between the WS connections and the HTTP request
    that triggers delivery to them."""
    previous = app.dependency_overrides.pop(dependency, None)
    try:
        yield
    finally:
        if previous is not None:
            app.dependency_overrides[dependency] = previous


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # lifespan binds these by name in src.main, so patch them there.
    async def fake_init() -> FakeRedis:
        return FakeRedis(decode_responses=True)

    async def fake_close(_redis: object) -> None:
        return None

    monkeypatch.setattr("src.main.init_redis", fake_init)
    monkeypatch.setattr("src.main.close_redis", fake_close)

    with (
        _without_override(get_redis_subscription_manager),
        TestClient(app) as test_client,
    ):
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

            # Chat creation only joins members' connections to chat_room on
            # a genuinely fresh create (see CreateChatUseCase) — a
            # session-scoped seeded database shared with other test files
            # may already have this exact pair's private chat from an
            # earlier file, in which case this POST just reuses it and
            # skips that join. Explicitly listing messages for both sides
            # (the same lazy join-on-view path the real frontend uses)
            # guarantees each socket is in the room regardless of whether
            # this run was the fresh-create — mirrors test_ws_typing.py's
            # _create_and_join_chat helper, which documents the same race.
            assert client.get(f"/api/v1/chats/{chat_id}/messages").status_code == 200
            _set_access_token(client, bob_token)
            assert client.get(f"/api/v1/chats/{chat_id}/messages").status_code == 200
            _set_access_token(client, alice_token)

            message_resp = client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"body": "hello over the wire"},
            )
            assert message_resp.status_code == 200

            # Wire shape unchanged: {"type": "message.created", "payload":
            # {...}} — the frontend's RealtimeProvider only reads these two
            # keys, so extra Envelope fields (room, event_id, ts) are safe
            # additions it silently ignores.
            for ws in (alice_ws, bob_ws):
                event = ws.receive_json()
                assert event["type"] == "message.created"
                payload = event["payload"]
                assert payload["body"] == "hello over the wire"
                assert payload["chat_id"] == chat_id
                assert payload["sender_id"] == str(ALICE_ID)


def test_reconnect_without_reviewing_the_chat_does_not_rejoin_its_room(
    client: TestClient,
) -> None:
    # Documents the accepted tradeoff of lazy join-on-view (see
    # messages.application.queries.list_chat_messages): connect-time no
    # longer bulk-joins every chat the user is already a member of, so a
    # membership that predates this connection isn't in the room index
    # until the user actually lists that chat's messages.
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    chat_resp = client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(BOB_ID)},
    )
    assert chat_resp.status_code == 201
    chat_id = UUID(chat_resp.json()["id"])

    _set_access_token(client, bob_token)
    # Snapshot inside the `with` block but assert after it exits cleanly:
    # an assertion raised while the socket is still open can deadlock
    # TestClient's shutdown (a pre-existing quirk unrelated to this
    # feature), so keep any possible failure outside the `with`.
    with client.websocket_connect("/api/v1/ws"):
        rooms_snapshot = set(app.state.connection_manager._rooms)

    assert f"chat:{chat_id}" not in rooms_snapshot
