from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from src.kernel.schemas.base_schema import BaseSchema


class ServerInvite(BaseSchema):
    id: UUID
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    created_at: datetime


class CreateServerInviteRequest(BaseSchema):
    expires_in: int | None = Field(None)
    max_uses: int | None = Field(
        default=None,
    )


class CreateServerInvite(BaseSchema):
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    expires_at: datetime | None


class ServerInviteWithStatus(ServerInvite):
    validity_status: Literal["valid", "expired", "exhausted"]
