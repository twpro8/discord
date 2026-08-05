from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class PresenceStatus(StrEnum):
    """Wire-level values, matching the Redis-stored status string and the
    frontend's PresenceEntry.status ("online"/"away"/"offline") with no
    translation layer, same rationale as EventType in core.realtime.envelope."""

    ONLINE = "online"
    AWAY = "away"
    OFFLINE = "offline"


@dataclass(frozen=True, kw_only=True)
class PresenceDTO:
    user_id: UUID
    status: PresenceStatus
    last_seen_at: datetime | None = None


@dataclass(frozen=True, kw_only=True)
class PresenceTransition:
    """Before/after aggregate status returned by every connection-lifecycle
    repository call, so PresenceService only fans out when `changed` is
    True instead of on every heartbeat."""

    old: PresenceStatus
    new: PresenceStatus

    @property
    def changed(self) -> bool:
        return self.old != self.new
