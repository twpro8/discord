from typing import Protocol
from uuid import UUID

from src.modules.calls.domain.entities.call_session import CallSession
from src.modules.calls.domain.enums import ReserveOutcome


class CallRepository(Protocol):
    """Redis-only, mirroring PresenceRepository's ephemeral-state shape —
    see modules.presence.domain.repositories.presence_repository. All
    mutating methods are built from atomic single-key `SET ... NX EX`
    operations (never a read-then-write check), so simultaneous callers
    can't both succeed at reserving the same user or winning the same
    accept race — see infrastructure.persistence.redis_call_repository
    and plan §1 for the full correctness argument, which mirrors
    RedisPresenceRepository's own documented reasoning for avoiding Lua.
    """

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
        """Atomically reserves both parties' active-call slots and creates
        the RINGING session. Returns CALLER_BUSY/CALLEE_BUSY, with no
        mutation retained, if that party already has an active call (the
        caller's own reservation is rolled back if the callee's fails —
        safe as a plain DELETE with no compare-and-delete needed, since
        only this call could be holding a key it just SET NX'd)."""
        ...

    async def get_session(self, call_id: UUID) -> CallSession | None: ...

    async def get_active_call_id_for_user(self, user_id: UUID) -> UUID | None:
        """Read-only lookup of a user's current active-call reservation,
        if any — used by disconnect handling to find which call (if any)
        a closing connection might be pinned to."""
        ...

    async def try_accept(
        self,
        call_id: UUID,
        connection_id: UUID,
        *,
        active_ttl_seconds: float,
    ) -> bool:
        """Atomic first-write-wins marker for the accept race (SET NX on a
        dedicated per-call marker key, keyed by whichever connection_id
        gets there first). On success, also pins answering_connection_id
        on the session, transitions state to ACTIVE, and extends the
        session's and both active-user reservations' TTLs. Returns False,
        with no mutation, if a different connection already won."""
        ...

    async def end_session(self, call_id: UUID) -> CallSession | None:
        """Deletes the session and both active-user reservations, and
        returns the session as it was (for building notification
        payloads) — or None if the session was already gone, so a
        double-hangup or a hangup racing a timeout is always safe."""
        ...
