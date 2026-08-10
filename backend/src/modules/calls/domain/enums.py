from enum import StrEnum


class CallState(StrEnum):
    """Wire-level values are irrelevant here (CallState never crosses the
    wire — only individual EventType values do), unlike PresenceStatus/
    EventType. Kept as a StrEnum anyway for cheap Redis (de)serialization
    and consistent logging."""

    RINGING = "ringing"
    ACTIVE = "active"


class ReserveOutcome(StrEnum):
    """Result of CallRepository.reserve(). RESERVED means both parties'
    active-call slots were atomically claimed and the RINGING session was
    created; the two *_BUSY values distinguish which party already had an
    active call, purely so the caller's client can show the right message
    (call.busy's `reason`) — never used for a correctness decision, which
    reserve()'s own atomicity already guarantees regardless of which value
    comes back."""

    RESERVED = "reserved"
    CALLER_BUSY = "caller_busy"
    CALLEE_BUSY = "callee_busy"
