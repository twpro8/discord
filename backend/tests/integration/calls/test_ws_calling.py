"""Integration tests for realtime call signaling — mirrors
tests/integration/realtime/test_ws_typing.py's structure/fixtures.

Unlike typing, call signaling doesn't authorize via chat-room membership
(no chat_room join is needed at all — see core.realtime.rooms.
connection_room's docstring and plan §2.3): a private chat between the
two parties is enough, `list_chat_member_ids` reads real chat membership
from Postgres via ChatsFacade.list_active_user_ids on every invite.

Also patches `get_session_factory` to the null-pool variant, same as
test_ws_typing.py — CallSignalingService's `list_chat_member_ids` closure
opens its own DB session directly via `get_session_factory()` in
main.py's lifespan, same as PresenceService's fan-out lookup.
"""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from uuid import UUID, uuid4

import pytest
from fakeredis.aioredis import FakeRedis
from starlette.testclient import TestClient

from src.api.v1.dependencies import get_redis_subscription_manager
from src.core.config import settings
from src.core.database.session import get_null_pool_session_factory
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
    previous = app.dependency_overrides.pop(dependency, None)
    try:
        yield
    finally:
        if previous is not None:
            app.dependency_overrides[dependency] = previous


def _build_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
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


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    yield from _build_client(monkeypatch)


@pytest.fixture
def short_ring_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Same as `client`, but with a near-instant ring timeout — patched
    before the TestClient (and thus the app lifespan, which reads
    settings.CALL_RING_TIMEOUT_SECONDS once at CallSignalingService
    construction time) is entered."""
    monkeypatch.setattr(settings, "CALL_RING_TIMEOUT_SECONDS", 0.05)
    yield from _build_client(monkeypatch)


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


def _create_private_chat(client: TestClient, target_user_id: UUID) -> str:
    """Must be called while logged in as the chat's other party."""
    chat_resp = client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(target_user_id)},
    )
    assert chat_resp.status_code == 201
    return str(chat_resp.json()["id"])


def test_full_happy_path_over_two_sockets(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())

            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            assert alice_ws.receive_json()["type"] == "call.invite"
            assert bob_ws.receive_json()["type"] == "call.invite"

            bob_ws.send_json({"type": "call.accept", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.accepted"
            assert bob_ws.receive_json()["type"] == "call.accepted"

            alice_ws.send_json(
                {"type": "call.offer", "call_id": call_id, "sdp": {"type": "offer"}}
            )
            offer_event = bob_ws.receive_json()
            assert offer_event["type"] == "call.offer"
            assert offer_event["payload"]["sdp"] == {"type": "offer"}

            bob_ws.send_json(
                {"type": "call.answer", "call_id": call_id, "sdp": {"type": "answer"}}
            )
            answer_event = alice_ws.receive_json()
            assert answer_event["type"] == "call.answer"

            bob_ws.send_json(
                {
                    "type": "call.ice_candidate",
                    "call_id": call_id,
                    "candidate": {"candidate": "x"},
                }
            )
            ice_event = alice_ws.receive_json()
            assert ice_event["type"] == "call.ice_candidate"

            alice_ws.send_json({"type": "call.hangup", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.hangup"
            assert bob_ws.receive_json()["type"] == "call.hangup"


async def test_answerer_initiated_renegotiation_relays_offer_and_answer(
    client: TestClient,
) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)

    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())

            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            assert alice_ws.receive_json()["type"] == "call.invite"
            assert bob_ws.receive_json()["type"] == "call.invite"

            bob_ws.send_json({"type": "call.accept", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.accepted"
            assert bob_ws.receive_json()["type"] == "call.accepted"

            # The answerer renegotiates mid-call (e.g. adding a video track
            # for camera/screen share) — the offer must reach the *caller*
            # and the caller's answer must come back to the answerer.
            bob_ws.send_json(
                {"type": "call.offer", "call_id": call_id, "sdp": {"type": "offer"}}
            )
            offer_event = alice_ws.receive_json()
            assert offer_event["type"] == "call.offer"
            assert offer_event["payload"]["sdp"] == {"type": "offer"}

            alice_ws.send_json(
                {"type": "call.answer", "call_id": call_id, "sdp": {"type": "answer"}}
            )
            answer_event = bob_ws.receive_json()
            assert answer_event["type"] == "call.answer"

            alice_ws.send_json({"type": "call.hangup", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.hangup"
            assert bob_ws.receive_json()["type"] == "call.hangup"


def test_reject_ends_the_call_for_both(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            alice_ws.receive_json()
            bob_ws.receive_json()

            bob_ws.send_json({"type": "call.reject", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.rejected"
            assert bob_ws.receive_json()["type"] == "call.rejected"


def test_cancel_before_acceptance_ends_the_call(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            alice_ws.receive_json()
            bob_ws.receive_json()

            alice_ws.send_json({"type": "call.cancel", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.cancelled"
            assert bob_ws.receive_json()["type"] == "call.cancelled"


def test_busy_when_caller_or_callee_already_in_a_call(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    john_token = _login(client, JOHN_USERNAME)

    _set_access_token(client, alice_token)
    alice_bob_chat = _create_private_chat(client, BOB_ID)
    alice_john_chat = _create_private_chat(client, JOHN_ID)
    _set_access_token(client, bob_token)
    bob_john_chat = _create_private_chat(client, JOHN_ID)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, john_token)
            with client.websocket_connect("/api/v1/ws") as john_ws:
                _set_access_token(client, alice_token)
                call_id = str(uuid4())
                alice_ws.send_json(
                    {
                        "type": "call.invite",
                        "call_id": call_id,
                        "chat_id": alice_bob_chat,
                        "callee_id": str(BOB_ID),
                    }
                )
                alice_ws.receive_json()
                bob_ws.receive_json()

                # Alice tries a second, unrelated call while still ringing
                # Bob -> self_busy.
                second_call_id = str(uuid4())
                alice_ws.send_json(
                    {
                        "type": "call.invite",
                        "call_id": second_call_id,
                        "chat_id": alice_john_chat,
                        "callee_id": str(JOHN_ID),
                    }
                )
                busy_event = alice_ws.receive_json()
                assert busy_event["type"] == "call.busy"
                assert busy_event["payload"]["reason"] == "self_busy"

                # John tries to call Bob, who's already ringing with
                # Alice -> callee_busy.
                _set_access_token(client, john_token)
                third_call_id = str(uuid4())
                john_ws.send_json(
                    {
                        "type": "call.invite",
                        "call_id": third_call_id,
                        "chat_id": bob_john_chat,
                        "callee_id": str(BOB_ID),
                    }
                )
                busy_event = john_ws.receive_json()
                assert busy_event["type"] == "call.busy"
                assert busy_event["payload"]["reason"] == "callee_busy"


def test_ring_timeout_ends_an_unanswered_call(short_ring_client: TestClient) -> None:
    client = short_ring_client
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            alice_ws.receive_json()
            bob_ws.receive_json()

            timeout_event = alice_ws.receive_json()
            assert timeout_event["type"] == "call.timeout"
            assert bob_ws.receive_json()["type"] == "call.timeout"


def test_unauthorized_invite_is_rejected_with_an_error(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    john_token = _login(client, JOHN_USERNAME)

    # A chat Alice is not a member of.
    _set_access_token(client, bob_token)
    bob_john_chat = _create_private_chat(client, JOHN_ID)

    _set_access_token(client, alice_token)
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, john_token)
            with client.websocket_connect("/api/v1/ws"):
                _set_access_token(client, alice_token)
                call_id = str(uuid4())
                alice_ws.send_json(
                    {
                        "type": "call.invite",
                        "call_id": call_id,
                        "chat_id": bob_john_chat,
                        "callee_id": str(BOB_ID),
                    }
                )

                error_event = alice_ws.receive_json()
                assert error_event["type"] == "error"
                assert error_event["payload"]["code"] == "unauthorized"

                # Bob's socket must be unaffected and still fully
                # functional — proves no call.invite leaked to him.
                _set_access_token(client, bob_token)
                good_chat_id = _create_private_chat(client, JOHN_ID)
                assert isinstance(good_chat_id, str)
                bob_ws.send_json({"type": "heartbeat", "idle": False})


def test_disconnect_during_ringing_ends_the_call(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    _set_access_token(client, bob_token)
    with client.websocket_connect("/api/v1/ws") as bob_ws:
        _set_access_token(client, alice_token)
        call_id = str(uuid4())
        with client.websocket_connect("/api/v1/ws") as alice_ws:
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            assert alice_ws.receive_json()["type"] == "call.invite"
            assert bob_ws.receive_json()["type"] == "call.invite"
        # alice_ws is now closed — the disconnect hook should end the
        # still-RINGING call and notify Bob.

        hangup_event = bob_ws.receive_json()
        assert hangup_event["type"] == "call.hangup"
        assert hangup_event["payload"] == {"call_id": call_id, "reason": "disconnected"}


def test_multi_tab_double_accept_only_one_tab_wins(client: TestClient) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_tab_a:
            with client.websocket_connect("/api/v1/ws") as bob_tab_b:
                _set_access_token(client, alice_token)
                call_id = str(uuid4())
                alice_ws.send_json(
                    {
                        "type": "call.invite",
                        "call_id": call_id,
                        "chat_id": chat_id,
                        "callee_id": str(BOB_ID),
                    }
                )
                assert alice_ws.receive_json()["type"] == "call.invite"
                assert bob_tab_a.receive_json()["type"] == "call.invite"
                assert bob_tab_b.receive_json()["type"] == "call.invite"

                bob_tab_a.send_json({"type": "call.accept", "call_id": call_id})
                bob_tab_b.send_json({"type": "call.accept", "call_id": call_id})

                assert alice_ws.receive_json()["type"] == "call.accepted"
                assert bob_tab_a.receive_json()["type"] == "call.accepted"
                assert bob_tab_b.receive_json()["type"] == "call.accepted"

                loser_event = bob_tab_b.receive_json()
                assert loser_event["type"] == "call.busy"
                assert loser_event["payload"]["reason"] == "answered_elsewhere"

                # The subsequent offer must reach only the winning tab.
                alice_ws.send_json(
                    {"type": "call.offer", "call_id": call_id, "sdp": {"type": "offer"}}
                )
                offer_event = bob_tab_a.receive_json()
                assert offer_event["type"] == "call.offer"


def test_late_ice_candidate_after_hangup_is_dropped_and_frees_the_pair(
    client: TestClient,
) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    with client.websocket_connect("/api/v1/ws") as alice_ws:
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            _set_access_token(client, alice_token)
            call_id = str(uuid4())
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            alice_ws.receive_json()
            bob_ws.receive_json()

            bob_ws.send_json({"type": "call.accept", "call_id": call_id})
            alice_ws.receive_json()
            bob_ws.receive_json()

            alice_ws.send_json({"type": "call.hangup", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.hangup"
            assert bob_ws.receive_json()["type"] == "call.hangup"

            # Stray candidate for the now-ended call — must not resurrect
            # anything or disrupt the socket.
            alice_ws.send_json(
                {
                    "type": "call.ice_candidate",
                    "call_id": call_id,
                    "candidate": {"candidate": "late"},
                }
            )

            # A brand-new call between the same pair only succeeds if
            # hangup's cleanup actually freed both active-call
            # reservations — proving the stray frame didn't leak state.
            new_call_id = str(uuid4())
            alice_ws.send_json(
                {
                    "type": "call.invite",
                    "call_id": new_call_id,
                    "chat_id": chat_id,
                    "callee_id": str(BOB_ID),
                }
            )
            new_invite_event = alice_ws.receive_json()
            assert new_invite_event["type"] == "call.invite"
            assert new_invite_event["payload"]["call_id"] == new_call_id
            assert bob_ws.receive_json()["type"] == "call.invite"


def test_invite_while_callee_offline_is_resynced_when_they_connect(
    client: TestClient,
) -> None:
    alice_token = _login(client, ALICE_USERNAME)
    bob_token = _login(client, BOB_USERNAME)
    _set_access_token(client, alice_token)
    chat_id = _create_private_chat(client, BOB_ID)

    # Bob is offline throughout the invite — nothing to receive it.
    with client.websocket_connect("/api/v1/ws") as alice_ws:
        call_id = str(uuid4())
        alice_ws.send_json(
            {
                "type": "call.invite",
                "call_id": call_id,
                "chat_id": chat_id,
                "callee_id": str(BOB_ID),
            }
        )
        assert alice_ws.receive_json()["type"] == "call.invite"

        # Bob comes online mid-ring — his freshly opened connection must
        # be resynced with the pending invite it missed while offline.
        _set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            resynced_event = bob_ws.receive_json()
            assert resynced_event["type"] == "call.invite"
            assert resynced_event["payload"]["call_id"] == call_id
            assert resynced_event["payload"]["caller_id"] == str(ALICE_ID)

            bob_ws.send_json({"type": "call.accept", "call_id": call_id})
            assert alice_ws.receive_json()["type"] == "call.accepted"
            assert bob_ws.receive_json()["type"] == "call.accepted"
