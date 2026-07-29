from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.domain.entity import Entity
from src.shared.schemas import BaseSchema


class ServerMember(Entity):
    def __init__(
        self,
        id: UUID,
        server_id: UUID,
        user_id: UUID,
        role: ServerMemberRole,
    ) -> None:
        super().__init__(id)
        self.server_id = server_id
        self.user_id = user_id
        self.role = role


class ServerMemberResponse(BaseSchema):
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
