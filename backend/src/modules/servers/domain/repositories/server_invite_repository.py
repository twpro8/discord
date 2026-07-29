from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from src.modules.servers.domain.entities.server_invite import (
    ServerInvite,
    ServerInviteCreate,
)


class ServerInviteRepository(Protocol):
    async def create(self, data: ServerInviteCreate) -> ServerInvite: ...
    async def get_one(self, **filter_by: Any) -> ServerInvite | None: ...
    async def delete(self, invite_id: UUID) -> None: ...
    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[ServerInvite]: ...
    async def increment_use_count_atomic(
        self,
        invite_id: UUID,
        max_uses: int | None,
    ) -> int: ...
