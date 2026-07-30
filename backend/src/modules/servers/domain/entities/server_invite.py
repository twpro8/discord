from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from src.shared.domain.entity import Entity


class ServerInvite(Entity):
    def __init__(
        self,
        id: UUID,
        server_id: UUID,
        code: str,
        created_by: UUID,
        max_uses: int | None,
        use_count: int,
        expires_at: datetime | None,
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self.server_id = server_id
        self.code = code
        self.created_by = created_by
        self.max_uses = max_uses
        self.use_count = use_count
        self.expires_at = expires_at
        self.created_at = created_at


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
