from typing import Any, Protocol
from uuid import UUID

from src.modules.servers.domain.entities.server_member import (
    ServerMember,
    ServerMemberCreate,
    ServerMemberUpdate,
)


class ServerMemberRepository(Protocol):
    async def create(self, data: ServerMemberCreate) -> ServerMember: ...
    async def get_one(self, **filter_by: Any) -> ServerMember | None: ...
    async def update(
        self,
        id_: UUID,
        data: ServerMemberUpdate,
        exclude_unset: bool = False,
    ) -> ServerMember: ...
