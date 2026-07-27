from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.common.schemas import BaseSchema
from src.modules.servers.enums import ServerMemberRole


class ServerSchema(BaseSchema):
    id: UUID
    name: str
    description: str | None
    icon_url: str | None
    owner_id: UUID
    member_count: int
    created_at: datetime
    updated_at: datetime


class ServerCreateRequestSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(..., max_length=300)


class ServerCreateSchema(ServerCreateRequestSchema):
    owner_id: UUID


class ServerUpdateRequestSchema(BaseSchema):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=300)


class ServerUpdateSchema(ServerUpdateRequestSchema):
    id: UUID
    owner_id: UUID


class UpdateOwnerIdSchema(BaseSchema):
    owner_id: UUID


class UpdateServerOwner(UpdateOwnerIdSchema):
    id: UUID


class ServerUserBriefSchema(BaseSchema):
    id: UUID
    name: str
    icon_url: str | None
    owner_id: UUID
    member_count: int
    role: ServerMemberRole
    joined_at: datetime


class ServerInviteCode(BaseSchema):
    code: str
