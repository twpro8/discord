import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for domain events raised inside an aggregate.

    These are internal to a bounded context. If another module needs to
    react to something that happened here, publish a dedicated
    *integration event* from application/integration_events instead of
    leaking this type across module boundaries.
    """

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
