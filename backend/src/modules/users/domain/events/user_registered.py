from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserRegisteredEvent(DomainEvent):
    """Raised inside the User aggregate when a new user registers.

    Internal to the `users` bounded context. If another module needs to
    react to a new user (e.g. send a welcome email), it subscribes to
    this event through the shared EventBus rather than importing
    `modules.users.domain` directly.
    """

    user_id: UUID
    email: str
