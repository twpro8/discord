"""Integration test proving presence fans out via server_room independently
of the friends path — Alice and John are co-members of a server but not
friends, exercising the plumbing added in
modules/servers/application/realtime.py + PresenceService's server-side
fan-out specifically (not covered by test_ws_presence.py, which only
exercises the friends path).
"""

from starlette.testclient import TestClient

from tests.integration.presence.conftest import (
    ALICE_ID,
    ALICE_USERNAME,
    login,
    set_access_token,
)

JOHN_USERNAME = "john"


def test_presence_fans_out_to_server_members_who_are_not_friends(
    client: TestClient,
) -> None:
    alice_token = login(client, ALICE_USERNAME)
    john_token = login(client, JOHN_USERNAME)
    server_id: str | None = None

    try:
        # John connects first so he's already listening when Alice's later
        # disconnect fires her offline transition.
        set_access_token(client, john_token)
        with client.websocket_connect("/api/v1/ws") as john_ws:
            set_access_token(client, alice_token)
            with client.websocket_connect("/api/v1/ws"):
                # Alice's own connection must already be open for her
                # create-time server_room join (published to her own
                # user_room) to land — otherwise it's a no-op per
                # DistributedRoomMembershipUpdater's documented tradeoff.
                set_access_token(client, alice_token)
                server_resp = client.post(
                    "/api/v1/servers", json={"name": "Presence Test Server"}
                )
                assert server_resp.status_code == 201
                server_id = server_resp.json()["id"]

                invite_resp = client.post(
                    f"/api/v1/servers/{server_id}/invites", json={}
                )
                assert invite_resp.status_code == 201
                code = invite_resp.json()["code"]

                # Likewise, John's connection must already be open for his
                # own join-time server_room join to land.
                set_access_token(client, john_token)
                join_resp = client.post("/api/v1/servers/join", json={"code": code})
                assert join_resp.status_code == 201

            # Alice's connection is now closed — her only one, so this is
            # a real online -> offline transition, fanned out via
            # server_room (not user_room — Alice and John share no
            # friendship).
            event = john_ws.receive_json()
            assert event["type"] == "presence.update"
            assert event["payload"]["user_id"] == str(ALICE_ID)
            assert event["payload"]["status"] == "offline"

        set_access_token(client, john_token)
        response = client.get(f"/api/v1/presence/servers/{server_id}")
        assert response.status_code == 200
        alice_entry = next(e for e in response.json() if e["user_id"] == str(ALICE_ID))
        assert alice_entry["status"] == "offline"
    finally:
        # Avoid leaving Alice and John as permanent co-members of a
        # leftover server in the shared seeded DB (this test creates a
        # fresh server every run — no cleanup would just accumulate them).
        if server_id is not None:
            set_access_token(client, alice_token)
            client.delete(f"/api/v1/servers/{server_id}")
