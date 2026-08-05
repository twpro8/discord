from typing import Any, Protocol
from uuid import UUID

from src.modules.servers.domain.entities.dtos import (
    ServerMemberCreate,
    ServerMemberUpdate,
    ServerMemberWithUser,
)
from src.modules.servers.domain.entities.server_member import ServerMember


class ServerMemberRepository(Protocol):
    async def create(self, data: ServerMemberCreate) -> ServerMember: ...
    async def get_one(self, **filter_by: Any) -> ServerMember | None: ...
    async def update(
        self,
        id_: UUID,
        data: ServerMemberUpdate,
    ) -> ServerMember: ...
    async def list_with_users(self, server_id: UUID) -> list[ServerMemberWithUser]: ...
    async def list_server_ids_for_user(self, user_id: UUID) -> set[UUID]: ...
    async def list_user_ids(self, server_id: UUID) -> set[UUID]: ...
