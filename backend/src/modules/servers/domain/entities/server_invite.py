from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from src.shared.domain.entity import Entity
from src.shared.schemas import BaseSchema


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


class ServerInviteResponse(BaseSchema):
    id: UUID
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    created_at: datetime


class ServerInviteCreateRequest(BaseSchema):
    expires_in: int | None = Field(None)
    max_uses: int | None = Field(default=None)


class ServerInviteCreate(BaseSchema):
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    expires_at: datetime | None


class ServerInviteWithStatus(BaseSchema):
    """Read-model DTO — independent of the ServerInvite entity (was a Pydantic
    subclass of it before ServerInvite became a rich entity)."""

    id: UUID
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    created_at: datetime
    validity_status: Literal["valid", "expired", "exhausted"]
