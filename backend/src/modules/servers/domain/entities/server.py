from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.domain.entity import Entity
from src.shared.domain.unset import UNSET, Unsettable


class Server(Entity):
    def __init__(
        self,
        id: UUID,
        name: str,
        description: str | None,
        icon_url: str | None,
        owner_id: UUID,
        member_count: int,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.description = description
        self.icon_url = icon_url
        self.owner_id = owner_id
        self.member_count = member_count
        self.created_at = created_at
        self.updated_at = updated_at


@dataclass(frozen=True, kw_only=True)
class ServerCreateData:
    """Mirrors the transport-layer create request; used as a Command field."""

    name: str
    description: str | None = None


@dataclass(frozen=True, kw_only=True)
class ServerCreate(ServerCreateData):
    """Persistence payload for a new server."""

    owner_id: UUID


@dataclass(frozen=True, kw_only=True)
class ServerUpdateData:
    """Mirrors the transport-layer update request; used as a Command field."""

    name: Unsettable[str] = UNSET
    description: Unsettable[str] = UNSET


@dataclass(frozen=True, kw_only=True)
class ServerUpdate(ServerUpdateData):
    """Persistence payload for a server update."""

    id: UUID
    owner_id: UUID


@dataclass(frozen=True, kw_only=True)
class ServerUserSummary:
    id: UUID
    name: str
    icon_url: str | None
    owner_id: UUID
    member_count: int
    role: ServerMemberRole
    joined_at: datetime
