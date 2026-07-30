from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.friends.domain.enums import FriendStatus
from src.shared.domain.unset import UNSET, Unsettable


@dataclass(frozen=True, kw_only=True)
class SendFriendRequestData:
    """Payload used to send a friend request by username."""

    username: str


@dataclass(frozen=True, kw_only=True)
class FriendRequestCreate:
    """Persistence payload for a new pending friend request."""

    user_id: UUID
    target_user_id: UUID
    status: FriendStatus = FriendStatus.PENDING


@dataclass(frozen=True, kw_only=True)
class FriendRequestUpdate:
    """Payload to update a friend request's status."""

    status: Unsettable[FriendStatus] = UNSET


@dataclass(frozen=True, kw_only=True)
class FriendRequestWithUser:
    id: UUID
    user_id: UUID
    target_user_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime

    username: str
    avatar_url: str | None
