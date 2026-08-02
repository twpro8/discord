from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from src.modules.servers.domain.entities.dtos import (
    ServerCreate,
    ServerUpdate,
    ServerUserSummary,
)
from src.modules.servers.domain.entities.server import Server


class ServerRepository(Protocol):
    async def create(self, data: ServerCreate) -> Server: ...
    async def get_one(self, **filter_by: Any) -> Server | None: ...
    async def update(
        self,
        server_id: UUID,
        data: ServerUpdate,
    ) -> Server: ...

    async def delete(self, server_id: UUID) -> None: ...
    async def decrement_member_count(self, server_id: UUID) -> Server: ...
    async def increment_count(self, server_id: UUID) -> Server: ...
    async def get_servers_where_user_is_member(
        self,
        user_id: UUID,
    ) -> list[ServerUserSummary]: ...
    async def get_server_where_user_is_member(
        self,
        user_id: UUID,
        server_id: UUID,
    ) -> Server | None: ...
    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[Server]: ...
