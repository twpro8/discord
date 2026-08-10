from collections.abc import Mapping
from typing import Any, Protocol

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.websocket.manager import ConnectionManager


class RealtimeNotifier(Protocol):
    """Fan-out of typed realtime events to WebSocket connections.

    Everything is a room — including a single user's own pseudo-room
    (see `core.realtime.rooms.user_room`), which is just a room like any
    other, not a distinct delivery mode. Callers who want to reach one
    user pass `user_room(user_id)`, same as any other room.

    Distinct from the domain EventBus: this is high-frequency realtime
    delivery to open sockets, not module-to-module domain events.
    """

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None: ...


class LocalRealtimeNotifier:
    """Delivers directly through this process's ConnectionManager.

    Correct — not just a stand-in — for single-instance deployments:
    within one process, local broadcast already reaches every connection
    that should receive the event. Cross-instance fan-out needs the
    Redis-backed notifier instead, so other instances' local connections
    can be reached too.
    """

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._connection_manager = connection_manager

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        envelope = Envelope(type=event_type, payload=dict(payload), room=room)
        await self._connection_manager.broadcast_to_room(room, envelope)


class RedisRealtimeNotifier:
    """Publishes through Redis so other instances' locally-connected
    sockets are reached too, not just this process's.

    Delivery back to *this* instance's own local connections happens the
    same way as any other instance's: RedisSubscriptionManager, subscribed
    to this room because it has a local subscriber, receives the publish
    back and calls ConnectionManager.broadcast_to_room — there's no direct
    local-delivery shortcut here, which keeps this instance's behavior
    identical to every other instance's rather than a special case.
    """

    def __init__(self, subscription_manager: RedisSubscriptionManager) -> None:
        self._subscription_manager = subscription_manager

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        envelope = Envelope(type=event_type, payload=dict(payload), room=room)
        await self._subscription_manager.publish(room, envelope)
