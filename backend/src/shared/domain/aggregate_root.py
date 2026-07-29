from uuid import UUID

from src.shared.domain.domain_event import DomainEvent
from src.shared.domain.entity import Entity


class AggregateRoot(Entity):
    """Entity that is the consistency boundary for a cluster of objects.

    Records domain events as it mutates so application code can pull and
    react to them (e.g. logging, follow-up side effects) after a
    successful commit, without the aggregate itself depending on how
    those events get handled.
    """

    def __init__(self, id: UUID) -> None:
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._domain_events
        self._domain_events = []
        return events
