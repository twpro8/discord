from typing import Any

from sqlalchemy import Row

from src.modules.servers.domain.entities.server import (
    ServerSchema,
    ServerUserBriefSchema,
)
from src.modules.servers.domain.entities.server_invite import ServerInvite
from src.modules.servers.domain.entities.server_member import ServerMemberSchema
from src.modules.servers.infrastructure.persistence.models import (
    ServerInviteOrm,
    ServerMemberOrm,
    ServerOrm,
)
from src.shared.repositories import BaseMapper


class ServerMapper(BaseMapper[ServerOrm, ServerSchema]):
    orm_class = ServerOrm
    schema_class = ServerSchema


class ServerUserBriefMapper(BaseMapper[ServerOrm, ServerUserBriefSchema]):
    orm_class = ServerOrm
    schema_class = ServerUserBriefSchema

    @classmethod
    def to_schema(cls, row: Row[Any] | ServerOrm) -> ServerUserBriefSchema:
        return cls.schema_class.model_validate(row)


class ServerMemberMapper(BaseMapper[ServerMemberOrm, ServerMemberSchema]):
    orm_class = ServerMemberOrm
    schema_class = ServerMemberSchema


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInvite]):
    orm_class = ServerInviteOrm
    schema_class = ServerInvite
