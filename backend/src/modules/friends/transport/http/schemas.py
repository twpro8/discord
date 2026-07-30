from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.modules.friends.domain.enums import FriendStatus
from src.shared.schemas import BaseSchema

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32


class SendFriendRequest(BaseSchema):
    """Payload used to send a friend request by username."""

    username: str = Field(
        min_length=MIN_USERNAME_LENGTH,
        max_length=MAX_USERNAME_LENGTH,
    )


class FriendRequestResponse(BaseSchema):
    """API response shape for a friend request."""

    id: UUID
    user_id: UUID
    target_user_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime


class FriendRequestWithUserResponse(BaseSchema):
    id: UUID
    user_id: UUID
    target_user_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime

    username: str
    avatar_url: str | None
