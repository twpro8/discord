import json
from collections.abc import Callable
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.envelope import EventType
from src.core.realtime.notifier import RealtimeNotifier
from src.core.realtime.rooms import chat_room

logger = get_logger(__name__)

IsConnectionInRoom = Callable[[UUID, str], bool]
"""Local, synchronous room-membership check — see
ConnectionManager.is_connection_in_room. Injected rather than importing
ConnectionManager directly, so TypingService stays testable with a plain
fake (same rationale as PresenceService's FanOutTargetsLookup)."""


class TypingService:
    """Stateless authenticated relay for chat typing indicators — no
    persistence, no TTL/sweep, no DB access at all. Staleness (crashed
    tab, dropped connection, missed explicit stop) is handled entirely
    client-side via a per-(chat,user) auto-expiry timer — see
    core.realtime.redis_pubsub.RedisSubscriptionManager's docstring,
    which explicitly anticipates typing needing no REST catch-up. Built
    once at app startup (main.py's lifespan), wired into
    ConnectionManager's activity callback alongside PresenceService.
    """

    def __init__(
        self,
        is_connection_in_room: IsConnectionInRoom,
        realtime_notifier: RealtimeNotifier,
    ) -> None:
        self._is_connection_in_room = is_connection_in_room
        self._notifier = realtime_notifier

    async def on_activity(
        self,
        user_id: UUID,
        connection_id: UUID,
        raw_text: str,
    ) -> None:
        """Fires on every inbound frame; anything that isn't a
        recognizable typing frame is silently ignored (matches
        presence's on_activity tolerance for frames it doesn't own)."""
        try:
            frame = _parse_typing_frame(raw_text)
            if frame is None:
                return
            chat_id, is_typing = frame
            room = chat_room(chat_id)
            if not self._is_connection_in_room(connection_id, room):
                return
            payload = {
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "is_typing": is_typing,
            }
            await self._notifier.publish_to_room(room, EventType.TYPING_UPDATE, payload)
        except Exception:
            logger.exception(
                "typing.on_activity_failed",
                user_id=str(user_id),
                connection_id=str(connection_id),
            )


def _parse_typing_frame(raw_text: str) -> tuple[UUID, bool] | None:
    # Broad except is deliberate here (not narrowed to specific exception
    # types): this repo's pinned ruff (0.15.22) has a formatter bug that
    # strips the required parentheses from a multi-exception
    # `except (A, B):` clause, silently producing invalid Python syntax —
    # confirmed by reproducing it in isolation. Any malformed/unexpected
    # frame is already meant to be treated as "not recognized" here, so a
    # single broad except is both correct and immune to that bug.
    try:
        data = json.loads(raw_text)
    except Exception:
        return None
    if not isinstance(data, dict) or data.get("type") != "typing":
        return None
    try:
        chat_id = UUID(str(data.get("chat_id")))
    except Exception:
        return None
    return chat_id, bool(data.get("is_typing", False))
