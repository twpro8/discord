from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class IceServer:
    """Mirrors the browser's RTCIceServer shape 1:1 (see
    frontend/src/features/calls/model/types.ts's IceServersResponse) so
    the transport layer can pass this straight through with no
    translation. `username`/`credential` are only set for TURN entries —
    STUN needs neither. The value in `credential` is an HMAC *output*
    (see application.turn_credentials), never TURN_SECRET_KEY itself,
    which never leaves the backend process."""

    urls: str
    username: str | None = None
    credential: str | None = None
