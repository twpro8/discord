from datetime import datetime
from uuid import UUID

from src.kernel.schemas.base_schema import BaseSchema
from src.modules.servers.enums import ServerMemberRole


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
