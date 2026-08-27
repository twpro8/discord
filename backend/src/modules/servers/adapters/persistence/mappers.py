from typing import Any, cast

from sqlalchemy import Row

from src.modules.servers.adapters.persistence.models import (
    ServerInviteOrm,
    ServerMemberOrm,
    ServerOrm,
)
from src.modules.servers.domain.entities.dtos import ServerUserSummary
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.entities.server_invite import ServerInvite
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.enums import ServerMemberRole


class ServerDataMapper:
    @staticmethod
    def to_entity(model: ServerOrm) -> Server:
        return Server(
            id=model.id,
            name=model.name,
            description=model.description,
            icon_url=model.icon_url,
            owner_id=model.owner_id,
            member_count=model.member_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ServerUserSummaryDataMapper:
    @staticmethod
    def to_entity(row: Row[Any]) -> ServerUserSummary:
        return ServerUserSummary(
            id=row.id,
            name=row.name,
            icon_url=row.icon_url,
            owner_id=row.owner_id,
            member_count=row.member_count,
            role=row.role,
            joined_at=row.joined_at,
        )


class ServerMemberDataMapper:
    @staticmethod
    def to_entity(model: ServerMemberOrm) -> ServerMember:
        return ServerMember(
            id=model.id,
            server_id=model.server_id,
            user_id=model.user_id,
            role=cast(ServerMemberRole, model.role),
        )


class ServerInviteDataMapper:
    @staticmethod
    def to_entity(model: ServerInviteOrm) -> ServerInvite:
        return ServerInvite(
            id=model.id,
            server_id=model.server_id,
            code=model.code,
            created_by=model.created_by,
            max_uses=model.max_uses,
            use_count=model.use_count,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )
