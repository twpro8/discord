from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.servers.domain.entities.server_member import ServerMemberSchema


class ServerMemberRepository(Protocol):
    async def create(self, data: BaseModel) -> ServerMemberSchema: ...
    async def get_one(self, **filter_by: Any) -> ServerMemberSchema | None: ...
    async def update(
        self,
        id_: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by: Any,
    ) -> ServerMemberSchema: ...
