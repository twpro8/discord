from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity


class Server(Entity):
    def __init__(
        self,
        id: UUID,
        name: str,
        description: str | None,
        icon_url: str | None,
        owner_id: UUID,
        member_count: int,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.description = description
        self.icon_url = icon_url
        self.owner_id = owner_id
        self.member_count = member_count
        self.created_at = created_at
        self.updated_at = updated_at
