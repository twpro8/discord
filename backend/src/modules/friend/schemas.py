"""Request and response schemas for friend requests."""

# Python modules
from datetime import datetime
from uuid import UUID

# Third-party modules
from pydantic import Field

# Project modules
from src.kernel.schemas import BaseSchema
from src.modules.friend.enums import FriendStatus

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32


class SendFriendRequest(BaseSchema):
    """Payload used to send a friend request by username."""

    username: str = Field(
        min_length=MIN_USERNAME_LENGTH,
        max_length=MAX_USERNAME_LENGTH,
    )


class FriendRequestCreate(BaseSchema):
    """Persistence payload for a new pending friend request."""

    user_id: UUID
    target_user_id: UUID
    status: FriendStatus = FriendStatus.PENDING


class FriendRequest(BaseSchema):
    """A persisted friend request."""

    id: UUID
    user_id: UUID
    target_user_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime


class FriendRequestUpdate(BaseSchema):
    """Payload to update a friend request's status."""

    status: FriendStatus


class FriendRequestWithUser(BaseSchema):
    id: UUID
    user_id: UUID
    target_user_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime

    username: str
    avatar_url: str | None
