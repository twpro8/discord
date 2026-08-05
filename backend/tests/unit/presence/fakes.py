from collections.abc import Mapping
from typing import Any
from uuid import UUID

from src.core.realtime.envelope import EventType
from src.modules.presence.domain.entities.dtos import (
    PresenceDTO,
    PresenceStatus,
    PresenceTransition,
)


class FakePresenceRepository:
    """Controllable fake for PresenceRepository — lets tests dictate the
    exact transition each call returns, rather than replicating Redis
    timing semantics (that's what test_redis_presence_repository.py, the
    real infra-layer test, is for)."""

    def __init__(self) -> None:
        self.record_connection_result = PresenceTransition(
            old=PresenceStatus.OFFLINE, new=PresenceStatus.ONLINE
        )
        self.remove_connection_result = PresenceTransition(
            old=PresenceStatus.ONLINE, new=PresenceStatus.OFFLINE
        )
        self.renew_connection_result = PresenceTransition(
            old=PresenceStatus.ONLINE, new=PresenceStatus.ONLINE
        )
        self.sweep_stale_result: list[UUID] = []
        self.statuses: dict[UUID, PresenceDTO] = {}
        self.renew_calls: list[tuple[UUID, UUID, bool]] = []
        self.raise_on_record = False
        self.raise_on_sweep = False

    async def record_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition:
        if self.raise_on_record:
            raise RuntimeError("boom")
        return self.record_connection_result

    async def remove_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition:
        return self.remove_connection_result

    async def renew_connection(
        self, user_id: UUID, connection_id: UUID, *, idle: bool
    ) -> PresenceTransition:
        self.renew_calls.append((user_id, connection_id, idle))
        return self.renew_connection_result

    async def get_statuses(self, user_ids: set[UUID]) -> dict[UUID, PresenceDTO]:
        return {uid: self.statuses[uid] for uid in user_ids if uid in self.statuses}

    async def list_online_user_ids(self) -> set[UUID]:
        return set(self.statuses.keys())

    async def sweep_stale(self) -> list[UUID]:
        if self.raise_on_sweep:
            raise RuntimeError("boom")
        return self.sweep_stale_result


class FakeRealtimeNotifier:
    def __init__(self) -> None:
        self.published: list[tuple[str, EventType, Mapping[str, Any]]] = []
        self.raise_for_rooms: set[str] = set()

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        if room in self.raise_for_rooms:
            raise RuntimeError("boom")
        self.published.append((room, event_type, dict(payload)))
