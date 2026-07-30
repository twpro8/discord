from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class RefreshToken(Entity):
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        is_revoked: bool,
        expires_at: datetime,
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.is_revoked = is_revoked
        self.expires_at = expires_at
        self.created_at = created_at
