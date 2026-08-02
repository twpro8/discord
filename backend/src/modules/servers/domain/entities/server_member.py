from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.domain.entity import Entity


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
