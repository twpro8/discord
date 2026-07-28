from datetime import datetime
from uuid import UUID

from src.shared.schemas import BaseSchema


class RefreshToken(BaseSchema):
    id: UUID
    user_id: UUID
    is_revoked: bool
    expires_at: datetime
    created_at: datetime
