import base64
import hashlib
import hmac

import pytest
from httpx import AsyncClient

from src.core.config import settings


@pytest.fixture(autouse=True)
def _reset_turn_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "STUN_URLS", "stun:stun.example.com:19302")
    monkeypatch.setattr(settings, "TURN_URLS", "")
    monkeypatch.setattr(settings, "TURN_SECRET_KEY", "")
    monkeypatch.setattr(settings, "TURN_CREDENTIAL_TTL_SECONDS", 3600.0)


async def test_returns_stun_only_when_turn_not_configured(
    authed_client: AsyncClient,
) -> None:
    response = await authed_client.get("/api/v1/calls/turn-credentials")

    assert response.status_code == 200
    body = response.json()
    assert body["ice_servers"] == [
        {"urls": "stun:stun.example.com:19302", "username": None, "credential": None}
    ]


async def test_returns_turn_entry_with_valid_hmac_when_configured(
    authed_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "TURN_URLS", "turn:turn.example.com:3478")
    monkeypatch.setattr(settings, "TURN_SECRET_KEY", "super-secret")

    response = await authed_client.get("/api/v1/calls/turn-credentials")

    assert response.status_code == 200
    ice_servers = response.json()["ice_servers"]
    assert len(ice_servers) == 2
    turn_entry = ice_servers[1]
    assert turn_entry["urls"] == "turn:turn.example.com:3478"
    assert turn_entry["username"] is not None
    assert turn_entry["credential"] is not None

    expected_digest = hmac.new(
        b"super-secret", turn_entry["username"].encode("utf-8"), hashlib.sha1
    ).digest()
    assert turn_entry["credential"] == base64.b64encode(expected_digest).decode("utf-8")

    # The secret itself must never appear anywhere in the response.
    assert "super-secret" not in response.text


async def test_unauthenticated_request_is_rejected(ac: AsyncClient) -> None:
    response = await ac.get("/api/v1/calls/turn-credentials")

    assert response.status_code == 401
