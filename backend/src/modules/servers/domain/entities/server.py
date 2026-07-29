from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.schemas import BaseSchema


class Server(BaseSchema):
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


class ServerCreate(ServerCreateRequest):
    owner_id: UUID


class ServerUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=300)


class ServerUpdate(ServerUpdateRequest):
    id: UUID
    owner_id: UUID


class UpdateOwnerID(BaseSchema):
    owner_id: UUID


class ServerUserSummary(BaseSchema):
    id: UUID
    name: str
    icon_url: str | None
    owner_id: UUID
    member_count: int
    role: ServerMemberRole
    joined_at: datetime


class ServerInviteCode(BaseSchema):
    code: str
