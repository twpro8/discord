from datetime import datetime
from uuid import UUID

from src.modules.presence.domain.entities.dtos import PresenceStatus
from src.shared.schemas import BaseSchema


class PresenceResponse(BaseSchema):
    user_id: UUID
    status: PresenceStatus
    last_seen_at: datetime | None
