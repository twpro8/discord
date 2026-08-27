"""Integration tests for realtime typing indicators — mirrors
tests/integration/realtime/test_ws.py's structure and fixtures.

TypingService authorizes a client-supplied chat_id via local, synchronous
room membership (see ConnectionManager.is_connection_in_room) rather than
a DB query, so these tests exercise the real room-join side effects of
chat creation and `GET /chats/{chat_id}/messages` (the lazy join-on-view),
same as test_ws.py's message fan-out tests do.

Also patches `get_session_factory` to the null-pool variant, same as
tests/integration/presence/conftest.py: every WS connect triggers
PresenceService's online/offline fan-out, which opens its own DB session
directly via `get_session_factory()` in main.py's lifespan closure (not
through the `get_session` FastAPI dependency the global test override
patches) — reusing the default pooled factory across more than one of
these WS-connecting tests hits asyncpg's "attached to a different loop"
error, since each test gets its own event loop but the pool's connections
were opened against a previous test's loop.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID

import pytest
from fakeredis.aioredis import FakeRedis
from starlette.testclient import TestClient

from src.api.v1.dependencies import get_redis_subscription_manager
from src.core.database.session import get_null_pool_session_factory
from src.core.realtime.rooms import chat_room
from src.main import app

ALICE_USERNAME = "alice"
BOB_USERNAME = "monica"
JOHN_USERNAME = "john"
PASSWORD = "12345678"

ALICE_ID = UUID("a2b3c4d5-e6f7-4a5b-8c9d-0e1f2a3b4c5d")
BOB_ID = UUID("1df5569d-c4bf-488e-9f0f-30946a7067c9")
JOHN_ID = UUID("c08386e7-bbab-43b4-8427-d296390a3e1e")


@contextmanager
def _without_override(dependency: Callable[..., object]) -> Iterator[None]:
    """conftest.py's global override hands get_realtime_notifier/
    get_room_membership_updater a fresh, throwaway RedisSubscriptionManager
    per call — these tests need the single real instance the lifespan
    creates on app.state, shared between the WS connections and the HTTP
    request that triggers delivery to them."""
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


def _create_private_chat(client: TestClient) -> str:
    chat_resp = client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(BOB_ID)},
    )
    assert chat_resp.status_code == 201
    return str(chat_resp.json()["id"])


def _create_and_join_chat(client: TestClient) -> str:
    """Must be called while logged in as Alice. Creates (or reuses) Alice
    & Bob's private chat, then has both list its messages so each of
    their *currently open* connections joins the chat's room.

    Chat creation only joins members' connections the first time a chat
    is actually created (see
    CreateChatUseCase._get_or_create_private_chat's early return
    for an already-existing chat) — the seeded test DB persists across
    test runs within a session, so a later test's "create" call usually
    hits that already-exists path instead of a fresh one, leaving that
    test's own fresh WS connections unjoined unless they separately list
    the chat's messages too. This mirrors the real frontend, which calls
    GET .../messages for whichever chat is open regardless of who is
    about to type — the sender needs their own connection joined to the
    room just as much as any recipient does (TypingService authorizes by
    the *sender's* room membership). Leaves the client authenticated as
    Bob.
    """
    chat_id = _create_private_chat(client)
    assert client.get(f"/api/v1/chats/{chat_id}/messages").status_code == 200

    _login(client, BOB_USERNAME)
    assert client.get(f"/api/v1/chats/{chat_id}/messages").status_code == 200
    return chat_id


def test_typing_update_fans_out_to_chat_room_members(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _login(client, ALICE_USERNAME)
            chat_id = _create_and_join_chat(client)

            alice_ws.send_json(
                {"type": "typing", "chat_id": chat_id, "is_typing": True}
            )
            event = bob_ws.receive_json()
            assert event["type"] == "typing.update"
            assert event["payload"] == {
                "chat_id": chat_id,
                "user_id": str(ALICE_ID),
                "is_typing": True,
            }

            alice_ws.send_json(
                {"type": "typing", "chat_id": chat_id, "is_typing": False}
            )
            event = bob_ws.receive_json()
            assert event["type"] == "typing.update"
            assert event["payload"] == {
                "chat_id": chat_id,
                "user_id": str(ALICE_ID),
                "is_typing": False,
            }


def test_typing_update_not_delivered_to_non_members(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    john_token = _login(client, JOHN_USERNAME)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, john_token)
            with client.websocket_connect("/api/v1/ws"):
                _login(client, ALICE_USERNAME)
                chat_id = _create_and_join_chat(client)

                # John never listed the chat's messages, so his
                # connection(s) were never joined to its room — confirmed
                # directly against ConnectionManager's internal state
                # rather than a blocking receive, which would hang forever
                # if correct (same idiom as
                # test_reconnect_without_reviewing_the_chat_does_not_rejoin_its_room
                # in test_ws.py).
                john_connection_ids = (
                    app.state.connection_manager._user_connections.get(JOHN_ID, set())
                )
                room_connection_ids = app.state.connection_manager._rooms.get(
                    chat_room(UUID(chat_id)), set()
                )
                assert john_connection_ids.isdisjoint(room_connection_ids)

                alice_ws.send_json(
                    {"type": "typing", "chat_id": chat_id, "is_typing": True}
                )
                event = bob_ws.receive_json()
                assert event["type"] == "typing.update"


def test_typing_frame_for_chat_the_sender_is_not_a_member_of_is_dropped(
    client: TestClient,
) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    john_token = _login(client, JOHN_USERNAME)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, john_token)
            with client.websocket_connect("/api/v1/ws") as john_ws:
                _login(client, ALICE_USERNAME)
                chat_id = _create_and_join_chat(client)

                # John isn't a member and never joined the room, so this
                # frame must be dropped — Bob should only ever see Alice's
                # legitimate typing frame that follows, never John's.
                john_ws.send_json(
                    {"type": "typing", "chat_id": chat_id, "is_typing": True}
                )
                alice_ws.send_json(
                    {"type": "typing", "chat_id": chat_id, "is_typing": True}
                )
                event = bob_ws.receive_json()
                assert event["payload"]["user_id"] == str(ALICE_ID)


def test_malformed_typing_frame_does_not_disconnect_the_socket(
    client: TestClient,
) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _login(client, ALICE_USERNAME)
            chat_id = _create_and_join_chat(client)

            alice_ws.send_text("not json at all {{{")
            alice_ws.send_json({"type": "typing", "is_typing": True})  # missing chat_id

            # The socket must still be usable afterward — a well-formed
            # frame right after the malformed ones still gets through.
            alice_ws.send_json(
                {"type": "typing", "chat_id": chat_id, "is_typing": True}
            )
            event = bob_ws.receive_json()
            assert event["type"] == "typing.update"
            assert event["payload"]["user_id"] == str(ALICE_ID)
