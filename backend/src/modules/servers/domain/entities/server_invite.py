from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class ServerInvite(Entity):
    def __init__(
        self,
        id: UUID,
        server_id: UUID,
        code: str,
        created_by: UUID,
        max_uses: int | None,
        use_count: int,
        expires_at: datetime | None,
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self.server_id = server_id
        self.code = code
        self.created_by = created_by
        self.max_uses = max_uses
        self.use_count = use_count
        self.expires_at = expires_at
        self.created_at = created_at
