import base64
import hashlib
import hmac
import time
from uuid import UUID

from src.core.config import settings
from src.modules.calls.domain.entities.dtos import IceServer


def build_ice_servers(user_id: UUID) -> list[IceServer]:
    """Pure, settings-driven computation — no DB/domain state, so the
    router calls this directly rather than dispatching a mediator
    query/command (same rationale as api.v1.health bypassing the
    mediator entirely). Returns STUN-only when TURN isn't configured
    (settings.turn_configured is False — the standard dev/test posture),
    or STUN+TURN with a freshly-minted, short-lived TURN credential
    otherwise. See plan §5.2/§5.3: STUN_URLS/TURN_URLS/TURN_SECRET_KEY
    are the single source of ICE server config — nothing is hardcoded on
    the frontend."""
    servers = [IceServer(urls=url) for url in _split_urls(settings.STUN_URLS)]
    if settings.turn_configured:
        username, credential = _mint_turn_credential(user_id)
        servers += [
            IceServer(urls=url, username=username, credential=credential)
            for url in _split_urls(settings.TURN_URLS)
        ]
    return servers


def _split_urls(raw: str) -> list[str]:
    return [url.strip() for url in raw.split(",") if url.strip()]


def _mint_turn_credential(user_id: UUID) -> tuple[str, str]:
    """TURN REST API convention (coturn's `use-auth-secret` mode): the
    username embeds an absolute expiry timestamp; the credential is an
    HMAC-SHA1 of that username, base64-encoded, keyed by a secret shared
    only with the TURN server (TURN_SECRET_KEY, set via env — see
    core.config.settings). coturn independently recomputes and compares
    this HMAC using the same secret, so no server-side session/revocation
    state is needed — the credential is simply invalid once its embedded
    expiry passes. TURN_SECRET_KEY itself is read only from settings
    here and never serialized into any response; only `username` and
    this HMAC *output* ever reach the client, via the transport schema
    (transport.http.schemas.IceServerResponse)."""
    expiry = int(time.time() + settings.TURN_CREDENTIAL_TTL_SECONDS)
    username = f"{expiry}:{user_id}"
    digest = hmac.new(
        settings.TURN_SECRET_KEY.encode("utf-8"),
        username.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    credential = base64.b64encode(digest).decode("utf-8")
    return username, credential
