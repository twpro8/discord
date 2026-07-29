from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from src.shared.schemas import BaseSchema


class ServerInvite(BaseSchema):
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


class ServerInviteWithStatus(ServerInvite):
    validity_status: Literal["valid", "expired", "exhausted"]
