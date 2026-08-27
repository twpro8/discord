import json
from collections.abc import Awaitable, Callable
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.envelope import EventType
from src.core.realtime.notifier import RealtimeNotifier
from src.core.realtime.rooms import server_room, user_room
from src.modules.presence.domain.entities.dtos import PresenceStatus
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)

logger = get_logger(__name__)

FanOutTargetsLookup = Callable[[UUID], Awaitable[tuple[set[UUID], set[UUID]]]]
"""Resolves a user's (friend_ids, server_ids) — who should learn about
their presence change. Injected rather than hardcoded so PresenceService
itself stays free of any DB/session dependency (see its docstring); the
production implementation (wired in main.py) opens its own short-lived
session via `get_session_factory()` and reads through `friends`'/`servers`'
facades, but PresenceService doesn't need to know that."""


class PresenceService:
    """Owns the connect/disconnect/heartbeat side of presence — deliberately
    **not** a use case built through FastAPI's per-request DI (see
    modules/presence/module docstring for why). Built once at app startup
    (main.py's lifespan), parallel to ConnectionManager/RedisSubscriptionManager,
    and called directly from api/v1/ws.py and ConnectionManager's
    `on_activity` callback rather than resolved via `Depends()`.

    FastAPI resolves WebSocket route dependencies against a `WebSocket`,
    never a `Request` — api/v1/dependencies.py's HTTP-facing use-case
    providers are typed `request: Request` throughout (via `SessionDep`
    and friends), so they don't resolve on a WS connection at all (this is
    also why core/websocket/auth.py hand-duplicates UserIdWSDep instead of
    reusing UserIdDep). Even if they did, the lifecycle doesn't fit: those
    providers build one session per HTTP request, but a WebSocket
    connection lives for hours and heartbeats fire every ~25s — routing
    those through a fresh use case+session each time would mean a DB round
    trip for an operation (a Redis ZADD) that needs no database access at
    all. `lookup_fan_out_targets` is only called on an actual transition
    (never on a plain heartbeat renewal that doesn't change the aggregate
    status), which is the whole point of this split.
    """

    def __init__(
        self,
        presence_repository: PresenceRepository,
        realtime_notifier: RealtimeNotifier,
        lookup_fan_out_targets: FanOutTargetsLookup,
    ) -> None:
        self._presence = presence_repository
        self._notifier = realtime_notifier
        self._lookup_fan_out_targets = lookup_fan_out_targets

    async def mark_connection_online(self, user_id: UUID, connection_id: UUID) -> None:
        try:
            transition = await self._presence.record_connection(user_id, connection_id)
            if transition.changed:
                await self._fan_out(user_id, transition.new)
        except Exception:
            logger.exception(
                "presence.mark_online_failed",
                user_id=str(user_id),
                connection_id=str(connection_id),
            )

    async def mark_connection_offline(self, user_id: UUID, connection_id: UUID) -> None:
        try:
            transition = await self._presence.remove_connection(user_id, connection_id)
            if transition.changed:
                await self._fan_out(user_id, transition.new)
        except Exception:
            logger.exception(
                "presence.mark_offline_failed",
                user_id=str(user_id),
                connection_id=str(connection_id),
            )

    async def on_activity(
        self, user_id: UUID, connection_id: UUID, raw_text: str
    ) -> None:
        """Wired directly as ConnectionManager's `on_activity` callback —
        fires on every inbound frame, not just heartbeats, so anything that
        isn't a recognizable `{"type":"heartbeat","idle":bool}` frame is
        treated as a liveness-only signal (idle=False) rather than erroring,
        matching `Connection.touch()`'s existing "any frame means alive"
        semantic."""
        try:
            idle = _parse_idle(raw_text)
            transition = await self._presence.renew_connection(
                user_id, connection_id, idle=idle
            )
            if transition.changed:
                await self._fan_out(user_id, transition.new)
        except Exception:
            logger.exception(
                "presence.renew_failed",
                user_id=str(user_id),
                connection_id=str(connection_id),
            )

    async def sweep_stale(self) -> None:
        try:
            transitioned = await self._presence.sweep_stale()
        except Exception:
            logger.exception("presence.sweep_failed")
            return
        for user_id in transitioned:
            await self._fan_out(user_id, PresenceStatus.OFFLINE)

    async def _fan_out(self, user_id: UUID, status: PresenceStatus) -> None:
        last_seen_at = None
        if status == PresenceStatus.OFFLINE:
            statuses = await self._presence.get_statuses({user_id})
            dto = statuses.get(user_id)
            last_seen_at = dto.last_seen_at if dto else None

        payload = {
            "user_id": str(user_id),
            "status": status.value,
            "last_seen_at": last_seen_at.isoformat() if last_seen_at else None,
        }

        try:
            friend_ids, server_ids = await self._lookup_fan_out_targets(user_id)
        except Exception:
            logger.exception("presence.fan_out_lookup_failed", user_id=str(user_id))
            return

        for friend_id in friend_ids:
            try:
                await self._notifier.publish_to_room(
                    user_room(friend_id), EventType.PRESENCE_UPDATE, payload
                )
            except Exception:
                logger.exception(
                    "presence.fan_out_failed",
                    user_id=str(user_id),
                    friend_id=str(friend_id),
                )

        for server_id in server_ids:
            try:
                await self._notifier.publish_to_room(
                    server_room(server_id), EventType.PRESENCE_UPDATE, payload
                )
            except Exception:
                logger.exception(
                    "presence.fan_out_failed",
                    user_id=str(user_id),
                    server_id=str(server_id),
                )


def _parse_idle(raw_text: str) -> bool:
    # Broad except is deliberate here (not narrowed to specific exception
    # types): this repo's pinned ruff (0.15.22) has a formatter bug that
    # strips the required parentheses from a multi-exception
    # `except (A, B):` clause, silently producing invalid Python syntax —
    # confirmed by reproducing it in isolation. Any malformed frame is
    # already meant to default to not-idle here, so a single broad except
    # is both correct and immune to that bug.
    try:
        data = json.loads(raw_text)
    except Exception:
        return False
    if not isinstance(data, dict) or data.get("type") != "heartbeat":
        return False
    return bool(data.get("idle", False))
