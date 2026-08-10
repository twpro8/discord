from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.core.realtime.envelope import EventType
from src.modules.calls.domain.entities.call_session import CallSession
from src.modules.calls.domain.enums import CallState, ReserveOutcome


class FakeRealtimeNotifier:
    """Same shape as tests.unit.typing.fakes.FakeRealtimeNotifier — kept
    colocated per this repo's convention of not centralizing per-module
    test fakes."""

    def __init__(self) -> None:
        self.published: list[tuple[str, EventType, Mapping[str, Any]]] = []
        self.raise_for_rooms: set[str] = set()

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        if room in self.raise_for_rooms:
            raise RuntimeError("boom")
        self.published.append((room, event_type, dict(payload)))


class FakeCallRepository:
    """In-memory stand-in for RedisCallRepository. Single-threaded Python
    execution makes every method here trivially atomic on its own, so
    this fake is for exercising CallSignalingService's *behavior* (which
    room gets which event, when a session is dropped) — the actual
    concurrency/atomicity guarantees are tested separately against the
    real Redis-backed implementation with fakeredis, see
    test_redis_call_repository.py."""

    def __init__(self) -> None:
        self.sessions: dict[UUID, CallSession] = {}
        self.active_user: dict[UUID, UUID] = {}
        self.accept_markers: dict[UUID, UUID] = {}

    async def reserve(
        self,
        call_id: UUID,
        chat_id: UUID,
        caller_id: UUID,
        callee_id: UUID,
        caller_connection_id: UUID,
        *,
        ring_ttl_seconds: float,
    ) -> ReserveOutcome:
        if caller_id in self.active_user:
            return ReserveOutcome.CALLER_BUSY
        if callee_id in self.active_user:
            return ReserveOutcome.CALLEE_BUSY
        self.active_user[caller_id] = call_id
        self.active_user[callee_id] = call_id
        self.sessions[call_id] = CallSession(
            call_id=call_id,
            chat_id=chat_id,
            caller_id=caller_id,
            callee_id=callee_id,
            caller_connection_id=caller_connection_id,
            answering_connection_id=None,
            state=CallState.RINGING,
            created_at=datetime.now(UTC),
        )
        return ReserveOutcome.RESERVED

    async def get_session(self, call_id: UUID) -> CallSession | None:
        return self.sessions.get(call_id)

    async def get_active_call_id_for_user(self, user_id: UUID) -> UUID | None:
        return self.active_user.get(user_id)

    async def try_accept(
        self,
        call_id: UUID,
        connection_id: UUID,
        *,
        active_ttl_seconds: float,
    ) -> bool:
        if call_id in self.accept_markers:
            return False
        session = self.sessions.get(call_id)
        if session is None:
            return False
        self.accept_markers[call_id] = connection_id
        self.sessions[call_id] = replace(
            session, answering_connection_id=connection_id, state=CallState.ACTIVE
        )
        return True

    async def end_session(self, call_id: UUID) -> CallSession | None:
        session = self.sessions.pop(call_id, None)
        if session is None:
            return None
        self.active_user.pop(session.caller_id, None)
        self.active_user.pop(session.callee_id, None)
        return session
