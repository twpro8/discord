from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from src.modules.servers.domain.enums import ServerMemberRole
from src.shared.domain.unset import UNSET, Unsettable


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


@dataclass(frozen=True, kw_only=True)
class ServerInviteCreateData:
    """Mirrors the transport-layer create request; used as a Command field."""

    expires_in: int | None = None
    max_uses: int | None = None


@dataclass(frozen=True, kw_only=True)
class ServerInviteCreate:
    """Persistence payload for a new server invite."""

    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    expires_at: datetime | None


@dataclass(frozen=True, kw_only=True)
class ServerInviteWithStatus:
    """Read-model DTO — independent of the ServerInvite entity (was a Pydantic
    subclass of it before ServerInvite became a rich entity)."""

    id: UUID
    server_id: UUID
    code: str
    created_by: UUID
    max_uses: int | None
    use_count: int
    expires_at: datetime | None
    created_at: datetime
    validity_status: Literal["valid", "expired", "exhausted"]


@dataclass(frozen=True, kw_only=True)
class ServerMemberCreate:
    server_id: UUID
    user_id: UUID
    role: ServerMemberRole = ServerMemberRole.member


@dataclass(frozen=True, kw_only=True)
class ServerMemberUpdate:
    role: Unsettable[ServerMemberRole] = UNSET


@dataclass(frozen=True, kw_only=True)
class ServerMemberWithUser:
    """Read-model DTO for the member roster — joins in user info the way
    `chats.ChatMemberSummary` does, since nothing needs this hydrated
    outside `servers` itself."""

    id: UUID
    user_id: UUID
    username: str
    avatar_url: str | None
    role: ServerMemberRole
