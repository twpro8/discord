from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol

from src.core.logging import get_logger
from src.shared.domain.domain_event import DomainEvent

logger = get_logger(__name__)

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(Protocol):
    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None: ...

    async def publish(self, event: DomainEvent) -> None: ...

    async def publish_many(self, events: Sequence[DomainEvent]) -> None: ...


class InMemoryEventBus:
    """Process-local EventBus: dispatches to subscribers registered on this
    instance, in-process, best-effort. Does not survive process restarts —
    swap in a durable adapter (e.g. Redis Streams) if a consumer needs that.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        logger.info(
            "domain_event.published",
            event_type=type(event).__name__,
            event_id=str(event.event_id),
        )
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
