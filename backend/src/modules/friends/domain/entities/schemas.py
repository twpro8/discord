from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.modules.friends.domain.enums import FriendStatus
from src.shared.domain.entity import Entity
from src.shared.schemas import BaseSchema

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


class FriendRequest(Entity):
    """A persisted friend request."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        target_user_id: UUID,
        status: FriendStatus,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at


class FriendRequestResponse(BaseSchema):
    """API response shape for a friend request."""

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
