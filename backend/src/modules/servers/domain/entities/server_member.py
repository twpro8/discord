from datetime import datetime
from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.schemas.base_schema import BaseSchema


class ServerMemberSchema(BaseSchema):
    id: UUID
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole


class ServerMemberCreateSchema(BaseSchema):
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole = ServerMemberRole.member


class ServerMemberUpdateSchema(BaseSchema):
    left_at: datetime | None = None


class UpdateMemberRole(BaseSchema):
    role: ServerMemberRole
