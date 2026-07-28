from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.servers.domain.entities.server import (
    ServerSchema,
    ServerUserBriefSchema,
)


class ServerRepository(Protocol):
    async def create(self, data: BaseModel) -> ServerSchema: ...
    async def get_one(self, **filter_by: Any) -> ServerSchema | None: ...
    async def update(
        self,
        id_: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by: Any,
    ) -> ServerSchema: ...
    async def delete(self, id_: UUID) -> None: ...
    async def decrement_member_count(self, server_id: UUID) -> ServerSchema: ...
    async def increment_count(self, server_id: UUID) -> ServerSchema: ...
    async def get_servers_where_user_is_member(
        self,
        user_id: UUID,
    ) -> list[ServerUserBriefSchema]: ...
    async def get_server_where_user_is_member(
        self,
        user_id: UUID,
        server_id: UUID,
    ) -> ServerSchema | None: ...
    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[ServerSchema]: ...
