from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.schemas import BaseSchema


class ServerMember(BaseSchema):
    id: UUID
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole


class ServerMemberCreate(BaseSchema):
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole = ServerMemberRole.member


class ServerMemberUpdate(BaseSchema):
    role: ServerMemberRole
