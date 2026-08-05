from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.schemas import BaseSchema


class ServerResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None
    icon_url: str | None
    owner_id: UUID
    member_count: int
    created_at: datetime
    updated_at: datetime


class ServerCreateRequest(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)


class ServerUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=300)


class UpdateOwnerID(BaseSchema):
    owner_id: UUID


class ServerUserSummaryResponse(BaseSchema):
    id: UUID
    name: str
    icon_url: str | None
    owner_id: UUID
    member_count: int
    role: ServerMemberRole
    joined_at: datetime


class ServerInviteCode(BaseSchema):
    code: str


class ServerMemberResponse(BaseSchema):
    id: UUID
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole


class ServerMemberWithUserResponse(BaseSchema):
    id: UUID
    user_id: UUID
    username: str
    avatar_url: str | None
    role: ServerMemberRole


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


class ServerInviteWithStatusResponse(BaseSchema):
    id: UUID
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    created_at: datetime
    validity_status: Literal["valid", "expired", "exhausted"]
