from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ChatCreatedEvent(DomainEvent):
    chat_id: UUID
