import json
from datetime import date, datetime
from typing import Any, Protocol
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.redis_pubsub import PubSubTransport

logger = get_logger(__name__)

TOPIC_PREFIX = "user"


def user_topic(user_id: UUID) -> str:
    """Redis pubsub topic a user's open WebSocket connections subscribe to."""
    return f"{TOPIC_PREFIX}:{user_id}:events"


class RealtimeNotifier(Protocol):
    """Fan-out of opaque payloads to a user's WebSocket connections.

    Distinct from the domain EventBus: this is high-frequency realtime
    delivery to open sockets, not module-to-module domain events.
    """

    async def publish_user_event(
        self, user_id: UUID, payload: dict[str, Any]
    ) -> None: ...


class RedisRealtimeNotifier:
    def __init__(self, transport: PubSubTransport) -> None:
        self._transport = transport

    async def publish_user_event(self, user_id: UUID, payload: dict[str, Any]) -> None:
        await self._transport.publish(
            user_topic(user_id),
            json.dumps(payload, default=_json_default),
        )


def _json_default(value: Any) -> str:
    """Serialize non-JSON values the way the REST layer does (ISO 8601)."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)
