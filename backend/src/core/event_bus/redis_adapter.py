import json
from collections import defaultdict
from collections.abc import Sequence

from redis.asyncio import Redis

from src.core.event_bus.bus import EventHandler
from src.core.logging import get_logger
from src.shared.domain.domain_event import DomainEvent

logger = get_logger(__name__)


class RedisStreamsEventBus:
    """Same EventBus Protocol shape as InMemoryEventBus (see bus.py) but
    durable: events survive a process restart, and — unlike in-process
    pub/sub — a consumer in a different process can subscribe to the same
    stream. This is the piece that changes on the day a module moves
    out-of-process; everything above core/ keeps depending on the EventBus
    Protocol and doesn't need to know which adapter is bound.
    """

    def __init__(self, client: Redis, stream_prefix: str = "events") -> None:
        self._client = client
        self._stream_prefix = stream_prefix
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def _stream_name(self, event_type: type[DomainEvent]) -> str:
        return (
            f"{self._stream_prefix}:{event_type.__module__}.{event_type.__qualname__}"
        )

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        # In-process registration for this worker's own consumer loop. A
        # real consumer loop (XREADGROUP against self._stream_name(...))
        # would run as a separate background task per subscribed type —
        # wire it in main.py's lifespan once a consumer actually needs it.
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        stream = self._stream_name(type(event))
        payload = json.dumps(event.__dict__, default=str)
        await self._client.xadd(stream, {"payload": payload})
        logger.info(
            "domain_event.published",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
            stream=stream,
        )
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
