from typing import Protocol
from uuid import UUID

from src.modules.presence.domain.entities.dtos import PresenceDTO, PresenceTransition


class PresenceRepository(Protocol):
    async def record_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition: ...

    async def remove_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition: ...

    async def renew_connection(
        self, user_id: UUID, connection_id: UUID, *, idle: bool
    ) -> PresenceTransition: ...

    async def get_statuses(self, user_ids: set[UUID]) -> dict[UUID, PresenceDTO]: ...

    async def list_online_user_ids(self) -> set[UUID]: ...

    async def sweep_stale(self) -> list[UUID]:
        """Purge stale connections across every currently-tracked user and
        return the ids of users that transitioned to OFFLINE as a result."""
        ...
