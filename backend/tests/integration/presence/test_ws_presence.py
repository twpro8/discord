"""Integration tests for presence fan-out to friends over the real
WebSocket + Redis stack (FakeRedis, see conftest.py). Mirrors
tests/integration/realtime/test_ws.py's structure and fixtures.
"""

from starlette.testclient import TestClient

from tests.integration.presence.conftest import (
    ALICE_ID,
    ALICE_USERNAME,
    BOB_USERNAME,
    login,
    set_access_token,
)


def _become_friends(client: TestClient, alice_token: str, bob_token: str) -> None:
    # Idempotent: the seeded test DB persists across tests within a
    # session (no per-test rollback), so a prior run of this test may have
    # already made Alice and Bob friends without reaching the cleanup at
    # the bottom (e.g. a failed assertion). A 409 here means a
    # relationship already exists (pending OR accepted) — verify it's the
    # latter rather than re-sending, which would 409 unconditionally.
    set_access_token(client, alice_token)
    response = client.post("/api/v1/friends/requests", json={"username": BOB_USERNAME})
    if response.status_code == 409:
        friends = client.get("/api/v1/friends")
        assert friends.status_code == 200
        assert any(f["username"] == BOB_USERNAME for f in friends.json())
        return

    assert response.status_code == 201
    request_id = response.json()["id"]

    set_access_token(client, bob_token)
    response = client.patch(f"/api/v1/friends/requests/{request_id}/accept")
    assert response.status_code == 200


def _remove_friendship(client: TestClient, alice_token: str) -> None:
    # Undoes _become_friends so this test doesn't leave Alice and Bob
    # permanently friended in the shared seeded DB — other integration
    # tests (e.g. tests/integration/realtime/test_ws.py, which also opens
    # WS connections for these two users) don't expect to receive
    # presence.update events interleaved with the ones they're asserting
    # on, which a lingering friendship would cause.
    set_access_token(client, alice_token)
    friends = client.get("/api/v1/friends")
    assert friends.status_code == 200
    relationship = next(
        (f for f in friends.json() if f["username"] == BOB_USERNAME), None
    )
    if relationship is not None:
        response = client.delete(f"/api/v1/friends/{relationship['id']}")
        assert response.status_code == 204


def test_presence_fans_out_online_and_offline_to_friends(client: TestClient) -> None:
    alice_token = login(client, ALICE_USERNAME)
    bob_token = login(client, BOB_USERNAME)
    _become_friends(client, alice_token, bob_token)

    try:
        # Bob connects first so he's already listening on his own
        # user_room when Alice's connect fires her online transition.
        set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            set_access_token(client, alice_token)
            with client.websocket_connect("/api/v1/ws") as alice_ws:  # noqa: F841
                event = bob_ws.receive_json()
                assert event["type"] == "presence.update"
                assert event["payload"]["user_id"] == str(ALICE_ID)
                assert event["payload"]["status"] == "online"
                assert event["payload"]["last_seen_at"] is None

            # alice_ws is now closed — her only connection, so this is a
            # real online -> offline transition, fanned out to Bob (her
            # friend).
            event = bob_ws.receive_json()
            assert event["type"] == "presence.update"
            assert event["payload"]["user_id"] == str(ALICE_ID)
            assert event["payload"]["status"] == "offline"
            assert event["payload"]["last_seen_at"] is not None

        # REST catch-up: a client that (re)connects later still sees
        # Alice as offline via GET /presence/friends, not just via the
        # dropped WS event.
        set_access_token(client, bob_token)
        response = client.get("/api/v1/presence/friends")
        assert response.status_code == 200
        alice_entry = next(e for e in response.json() if e["user_id"] == str(ALICE_ID))
        assert alice_entry["status"] == "offline"
        assert alice_entry["last_seen_at"] is not None
    finally:
        _remove_friendship(client, alice_token)


def test_idle_heartbeat_transitions_status_to_away_and_back(
    client: TestClient,
) -> None:
    alice_token = login(client, ALICE_USERNAME)
    bob_token = login(client, BOB_USERNAME)
    _become_friends(client, alice_token, bob_token)

    try:
        set_access_token(client, bob_token)
        with client.websocket_connect("/api/v1/ws") as bob_ws:
            set_access_token(client, alice_token)
            with client.websocket_connect("/api/v1/ws") as alice_ws:
                online_event = bob_ws.receive_json()
                assert online_event["payload"]["status"] == "online"

                alice_ws.send_json({"type": "heartbeat", "idle": True})
                away_event = bob_ws.receive_json()
                assert away_event["type"] == "presence.update"
                assert away_event["payload"]["user_id"] == str(ALICE_ID)
                assert away_event["payload"]["status"] == "away"

                alice_ws.send_json({"type": "heartbeat", "idle": False})
                online_again_event = bob_ws.receive_json()
                assert online_again_event["payload"]["status"] == "online"
    finally:
        _remove_friendship(client, alice_token)
