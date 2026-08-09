from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.calls.domain.enums import CallState


@dataclass(frozen=True, kw_only=True)
class CallSession:
    """Ephemeral, Redis-only — no persistence identity, so this is a plain
    dataclass rather than an Entity/AggregateRoot (see shared.domain).
    caller_connection_id is pinned at invite time and answering_connection_id
    at accept time, both taken from the server's own observation of which
    connection sent the relevant frame (ConnectionManager.serve()'s reader
    loop passes connection_id for free) — never client-reported. See
    plan §2.4 for why no other tab-identifying data is needed."""

    call_id: UUID
    chat_id: UUID
    caller_id: UUID
    callee_id: UUID
    caller_connection_id: UUID
    answering_connection_id: UUID | None
    state: CallState
    created_at: datetime
