import base64
import hashlib
import hmac
from uuid import uuid4

import pytest

from src.core.config import settings
from src.modules.calls.application.turn_credentials import build_ice_servers


@pytest.fixture(autouse=True)
def _reset_turn_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "STUN_URLS", "stun:stun.example.com:19302")
    monkeypatch.setattr(settings, "TURN_URLS", "")
    monkeypatch.setattr(settings, "TURN_SECRET_KEY", "")
    monkeypatch.setattr(settings, "TURN_CREDENTIAL_TTL_SECONDS", 3600.0)


def test_returns_stun_only_when_turn_not_configured() -> None:
    servers = build_ice_servers(uuid4())

    assert len(servers) == 1
    assert servers[0].urls == "stun:stun.example.com:19302"
    assert servers[0].username is None
    assert servers[0].credential is None


def test_returns_stun_and_turn_with_valid_hmac_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings, "TURN_URLS", "turn:turn.example.com:3478,turns:turn.example.com:5349"
    )
    monkeypatch.setattr(settings, "TURN_SECRET_KEY", "super-secret")
    user_id = uuid4()

    servers = build_ice_servers(user_id)

    assert len(servers) == 3
    stun, turn1, turn2 = servers
    assert stun.urls == "stun:stun.example.com:19302"
    assert stun.username is None

    for turn_server in (turn1, turn2):
        assert turn_server.username is not None
        assert turn_server.credential is not None
        # Independently recompute the HMAC coturn would verify against —
        # confirms the credential is exactly what the shared secret
        # produces, without ever needing the secret itself to leave the
        # backend (it's read only from settings here).
        expected_digest = hmac.new(
            b"super-secret", turn_server.username.encode("utf-8"), hashlib.sha1
        ).digest()
        expected_credential = base64.b64encode(expected_digest).decode("utf-8")
        assert turn_server.credential == expected_credential

        expiry_str, embedded_user_id = turn_server.username.split(":", 1)
        assert embedded_user_id == str(user_id)
        assert int(expiry_str) > 0

    assert turn1.urls == "turn:turn.example.com:3478"
    assert turn2.urls == "turns:turn.example.com:5349"
    # Same secret/TTL/user within the same second -> identical credential.
    assert turn1.username == turn2.username
    assert turn1.credential == turn2.credential


def test_credential_differs_per_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TURN_URLS", "turn:turn.example.com:3478")
    monkeypatch.setattr(settings, "TURN_SECRET_KEY", "super-secret")

    servers_a = build_ice_servers(uuid4())
    servers_b = build_ice_servers(uuid4())

    assert servers_a[1].credential != servers_b[1].credential
